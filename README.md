## ACES Auto Color Space [blender addon]

**Version:** 1.4  
**Blender:** 4.2.0+  
**Author:** ChatGPT

---

### 📝 Description (EN)
ACES Auto Color Space is a Blender add-on that automatically assigns the correct Color Space for Image and Environment Texture nodes when using ACES color management. It scans through materials, world nodes, and nested NodeGroups, and sets:

- **HDR maps** (`.exr`, `.hdr`, `.pfm`) → **Utility - Linear - sRGB**
- **Color textures** (Albedo, Diffuse, Translucency, etc.) → **Utility - sRGB - Texture**
- **Raw data maps** (Normal, Roughness, Metallic, AO, Mask, Gloss, Falloff, etc.) → **Utility - Raw**

Save time by eliminating manual color space adjustments and streamline your ACES-based workflow!

### ⚙️ Installation (EN)
1. Download or clone this repository.
2. Open **Blender → Preferences → Add-ons**.
3. Click **Install...**, navigate to `aces_auto_colorspace.py` and install.
4. Enable the add-on in the list.
5. In **Shader Editor** (Node Editor), open the **ACES** tab in the sidebar.
6. Click **Auto ACES Color Space** to process all textures.

### 🚀 Usage (EN)
- Works in all materials and world node trees, including nested NodeGroups.
- Automatically detects texture type by filename, node name, or label.
- Reports the number of nodes updated in the Info panel.

### 📄 License (EN)
This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

## ACES Auto Color Space

**Версия:** 1.4  
**Blender:** 4.2.0+  
**Автор:** ChatGPT

---

### 📝 Описание (RU)
ACES Auto Color Space — аддон для Blender, который автоматически назначает корректный Color Space для узлов Image и Environment Texture при использовании ACES color management. Аддон:

- Сканирует материалы, узлы мира и вложенные NodeGroup.
- Назначает:
  - **HDR (exr, hdr, pfm)** → **Utility - Linear - sRGB**
  - **Цветовые текстуры** (Albedo, Diffuse, Translucency и т.д.) → **Utility - sRGB - Texture**
  - **Raw-данные** (Normal, Roughness, Metallic, AO, Mask, Gloss, Falloff и т.д.) → **Utility - Raw**

Исключает ручную корректировку цветового пространства и ускоряет работу с ACES.

### ⚙️ Установка (RU)
1. Скачайте или склонируйте репозиторий.
2. В Blender перейдите **Edit → Preferences → Add-ons**.
3. Нажмите **Install...** и выберите файл `aces_auto_colorspace.py`.
4. Активируйте аддон в списке.
5. В **Shader Editor** откройте вкладку **ACES** в боковой панели.
6. Нажмите **Auto ACES Color Space** для обработки текстур.

### 🚀 Использование (RU)
- Работает для всех материалов и деревьев узлов мира, включая вложенные группы.
- Определяет тип текстуры по имени файла, имени узла или метке.
- Выводит количество обновлённых узлов в панели Info.

### 📄 Лицензия (RU)
Проект распространяется под лицензией MIT. Подробности в файле [LICENSE](LICENSE).

