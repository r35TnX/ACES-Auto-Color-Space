bl_info = {
    "name": "ACES Auto Color Space",
    "author": "ChatGPT",
    "version": (1, 4),
    "blender": (4, 2, 0),
    "location": "Node Editor > Sidebar > ACES",
    "description": "Автоматически переназначает Color Space для Image и Environment Texture узлов под ACES, включая NodeGroup и разные типы текстур",
    "category": "Node",
}

import bpy

# Определение типа текстуры по имени файла/узла

def detect_texture_type(node):
    """
    Возвращает 'hdr', 'raw' или 'color' на основе расширения файла и ключевых слов.
    """
    if not hasattr(node, 'image') or not node.image:
        return None
    fname = bpy.path.abspath(node.image.filepath).lower()
    lname = (node.name or "").lower()
    llabel = (node.label or "").lower()

    # HDR по расширению
    if fname.endswith(('.exr', '.hdr', '.pfm')):
        return 'hdr'

    # Ключевые слова для raw-данных
    raw_keys = [
        'normal', 'nrml',
        'normal bump', 'normal object',
        'displacement', 'disp', 'bump',
        'rough', 'roughness',
        'metal', 'metalness',
        'specular', 'spec',
        'cavity', 'curvature',
        'glossiness', 'gloss',
        'fuzz',
        'occlusion', 'ao',
        'mask',
        'falloff',
        'thickness',
        'opacity',
        'brush',
        'transmission',
        'alpha',
        'dirtmap', 'dirt'
    ]
    for key in raw_keys:
        if key in fname or key in lname or key in llabel:
            return 'raw'

    # Ключевые слова для цветовых текстур
    color_keys = [
        'albedo',
        'diffuse',
        'translucency'
    ]
    for key in color_keys:
        if key in fname or key in lname or key in llabel:
            return 'color'

    # По умолчанию считаем цветовой текстурой
    return 'color'


def map_colorspace(tex_type):
    """
    Возвращает строку Color Space для ACES.
    """
    if tex_type == 'hdr':
        return 'Utility - Linear - sRGB'
    elif tex_type == 'color':
        return 'Utility - sRGB - Texture'
    elif tex_type == 'raw':
        return 'Utility - Raw'
    return None


def process_node_tree(node_tree):
    """
    Рекурсивно обрабатывает узлы в данном node_tree, включая группы.
    Возвращает количество изменённых узлов.
    """
    changed = 0
    for node in node_tree.nodes:
        # Если это группа, обрабатываем её внутрянку
        if isinstance(node, bpy.types.ShaderNodeGroup) and node.node_tree:
            changed += process_node_tree(node.node_tree)
        # Проверяем Image и Environment текстуры
        if isinstance(node, (bpy.types.ShaderNodeTexImage, bpy.types.ShaderNodeTexEnvironment)) and node.image:
            tex_type = detect_texture_type(node)
            cs = map_colorspace(tex_type)
            if cs and node.image.colorspace_settings.name != cs:
                node.image.colorspace_settings.name = cs
                changed += 1
    return changed


class ACES_OT_auto_colorspace(bpy.types.Operator):
    bl_idname = "node.aces_auto_colorspace"
    bl_label = "Auto ACES Color Space"
    bl_description = "Переназначить Color Space для всех Image/Environment Texture узлов под ACES, включая NodeGroup"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        changed = 0
        # Обрабатывать материалы
        for mat in bpy.data.materials:
            if mat.use_nodes and mat.node_tree:
                changed += process_node_tree(mat.node_tree)
        # Обрабатывать миры
        for world in bpy.data.worlds:
            if world.use_nodes and world.node_tree:
                changed += process_node_tree(world.node_tree)

        self.report({'INFO'}, f"ACES Auto Color Space: переназначено {changed} узлов")
        return {'FINISHED'}


class ACES_PT_panel(bpy.types.Panel):
    bl_label = "ACES Color Space"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'ACES'

    def draw(self, context):
        layout = self.layout
        layout.operator(ACES_OT_auto_colorspace.bl_idname, icon='COLOR')


classes = [ACES_OT_auto_colorspace, ACES_PT_panel]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
