bl_info = {
    "name": "ACES Auto Color Space",
    "author": "ChatGPT & User",
    "version": (1, 5),
    "blender": (4, 5, 0),
    "location": "Node Editor > Sidebar > ACES",
    "description": "Автоматически переназначает Color Space для Image/Environment узлов под ACES с проверкой ошибок",
    "category": "Node",
}

import bpy

class AcesLogic:
    """Класс для инкапсуляции логики определения типов текстур"""

    # Ключевые слова вынесены в атрибуты класса для удобства редактирования
    RAW_KEYS = {
        'normal', 'nrml', 'normal bump', 'normal object',
        'displacement', 'disp', 'bump', 'height',
        'rough', 'roughness', 'glossiness', 'gloss',
        'metal', 'metalness', 'metallic',
        'specular', 'spec', 'reflection',
        'cavity', 'curvature',
        'occlusion', 'ao', 'ambocc',
        'mask', 'id', 'opacity', 'alpha',
        'transparency', 'transmission',
        'flow', 'vector'
    }

    COLOR_KEYS = {
        'albedo', 'diffuse', 'color', 'basecolor',
        'base_color', 'emit', 'emission', 'translucency', 'sss'
    }

    # Маппинг типов на имена ACES (можно настроить под конкретный конфиг)
    ACES_MAPPING = {
        'hdr': 'Utility - Linear - sRGB',
        'raw': 'Utility - Raw',
        'color': 'Utility - sRGB - Texture'
    }

    @staticmethod
    def detect_texture_type(node):
        """Возвращает 'hdr', 'raw' или 'color'."""
        if not node.image:
            return None

        # Безопасное получение пути и имени
        filepath = node.image.filepath.lower()
        # Используем abspath для корректной работы с относительными путями
        fname = bpy.path.basename(filepath)

        lname = (node.name or "").lower()
        llabel = (node.label or "").lower()

        # Собираем все строки, где может быть имя, в один список для проверки
        search_strings = [fname, lname, llabel]

        # 1. Проверка на HDR
        if filepath.endswith(('.exr', '.hdr', '.pfm')):
            return 'hdr'

        # 2. Проверка на RAW данные
        for s in search_strings:
            if any(key in s for key in AcesLogic.RAW_KEYS):
                return 'raw'

        # 3. Проверка на Color данные
        for s in search_strings:
            if any(key in s for key in AcesLogic.COLOR_KEYS):
                return 'color'

        # Fallback по умолчанию
        return 'color'

    @classmethod
    def get_target_colorspace(cls, node):
        tex_type = cls.detect_texture_type(node)
        return cls.ACES_MAPPING.get(tex_type)


def get_available_colorspaces(image):
    """Возвращает список доступных цветовых пространств для данного изображения"""
    if not image or not image.colorspace_settings:
        return set()
    # Получаем список enum items
    return {item.identifier for item in image.colorspace_settings.bl_rna.properties['name'].enum_items}


def process_node_tree(node_tree, available_spaces_cache, processed_trees):
    """
    Рекурсивная обработка с защитой от циклов.
    available_spaces_cache: словарь {image_name: {set_of_spaces}} для оптимизации
    processed_trees: множество {tree_pointer} для избежания повторной обработки
    """
    if node_tree in processed_trees:
        return 0

    processed_trees.add(node_tree)
    changed_count = 0

    for node in node_tree.nodes:
        # Рекурсия для групп
        if isinstance(node, bpy.types.ShaderNodeGroup) and node.node_tree:
            changed_count += process_node_tree(node.node_tree, available_spaces_cache, processed_trees)
            continue

        # Обработка текстур
        if isinstance(node, (bpy.types.ShaderNodeTexImage, bpy.types.ShaderNodeTexEnvironment)) and node.image:
            target_cs = AcesLogic.get_target_colorspace(node)

            if not target_cs:
                continue

            current_cs = node.image.colorspace_settings.name

            # Если уже стоит нужный спейс - пропускаем
            if current_cs == target_cs:
                continue

            # Проверка: существует ли такой спейс в конфиге Blender?
            # Кэшируем список доступных спейсов для этой картинки, чтобы не дергать API каждый раз
            img_key = node.image.name
            if img_key not in available_spaces_cache:
                available_spaces_cache[img_key] = get_available_colorspaces(node.image)

            if target_cs in available_spaces_cache[img_key]:
                node.image.colorspace_settings.name = target_cs
                changed_count += 1
            else:
                print(f"[ACES Addon Warning] Space '{target_cs}' not found for image '{node.image.name}'. Check your OCIO config.")

    return changed_count


class ACES_OT_auto_colorspace(bpy.types.Operator):
    bl_idname = "node.aces_auto_colorspace"
    bl_label = "Auto ACES Color Space"
    bl_description = "Переназначить Color Space под ACES (включая группы и под-материалы)"
    bl_options = {'REGISTER', 'UNDO'} # ВАЖНО: Позволяет делать Ctrl+Z

    @classmethod
    def poll(cls, context):
        return context.space_data.type == 'NODE_EDITOR'

    def execute(self, context):
        changed_total = 0
        processed_trees = set() # Защита от повторной обработки одной и той же группы
        available_spaces_cache = {} # Кэш доступных колорспейсов

        # 1. Обрабатываем Материалы
        for mat in bpy.data.materials:
            # Пропускаем linked данные (библиотечные), их нельзя менять
            if mat.library:
                continue
            if mat.use_nodes and mat.node_tree:
                changed_total += process_node_tree(mat.node_tree, available_spaces_cache, processed_trees)

        # 2. Обрабатываем Миры (Worlds)
        for world in bpy.data.worlds:
            if world.library:
                continue
            if world.use_nodes and world.node_tree:
                changed_total += process_node_tree(world.node_tree, available_spaces_cache, processed_trees)

        if changed_total > 0:
            self.report({'INFO'}, f"ACES: Обновлено {changed_total} узлов.")
        else:
            self.report({'WARNING'}, "ACES: Изменений не требуется или нужный Color Space не найден.")

        return {'FINISHED'}


class ACES_PT_panel(bpy.types.Panel):
    bl_label = "ACES Utils"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'ACES'

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.operator(ACES_OT_auto_colorspace.bl_idname, icon='COLOR')

        # Дополнительная инфо
        if context.scene.display_settings.display_device != 'ACES':
            layout.separator()
            box = layout.box()
            box.label(text="Внимание: ACES не активен", icon='ERROR')
            box.label(text="в настройках Color Management")


classes = [ACES_OT_auto_colorspace, ACES_PT_panel]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
