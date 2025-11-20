# AppImage2Desktop

## AppImage 桌面集成工具

本程序提供图形用户界面（GUI），可轻松将 AppImage 应用集成至 Plasma (KDE) 桌面环境。通过创建相应的 `.desktop` 文件，您可以让 AppImage 应用以正确的名称、描述和图标显示在系统的程序启动器中。

## 功能特性

- **选择 AppImage：** 浏览并选择您本地的 AppImage 文件。
- **自动提取信息：** 从 AppImage 内置的 `.desktop` 文件中自动提取并填充应用名称、注释、图标和分类等信息，简化集成过程。
- **自定义条目：** 如有需要，可以手动修改应用名称、描述、图标路径和分类。
- **提取图标：** 如果 AppImage 内置的 `.desktop` 文件指定了图标，程序会自动提取该图标并保存到 `~/.local/share/icons/` 目录。
- **生成桌面文件：** 在 `~/.local/share/applications/` 目录下创建 `.desktop` 文件，实现与桌面环境的无缝集成。
- **设置执行权限：** 自动为 AppImage 文件和生成的 `.desktop` 文件添加可执行权限。

## 使用方法

1.  **运行程序：**
    ```bash
    python3 main.py
    ```
2.  **选择 AppImage 文件：** 点击 “Browse...” 按钮，选择您要集成的 AppImage 文件。
3.  **提取信息（推荐）：** 点击 “Extract & Populate” 按钮，程序将执行以下操作：
    *   将 AppImage 的内容提取到临时位置。
    *   在提取的内容中查找 `.desktop` 文件。
    *   如果找到，则读取应用的名称、注释和图标信息，并自动填充到界面中。
    *   程序会尝试提取并保存图标至 `~/.local/share/icons/`，然后更新界面上的“Icon”路径。
4.  **检查与自定义：** 检查 “App Name”、“Description”、“Icon” 和 “Category” 字段的内容。如果自动提取的信息不完整，或您想使用其他图标，可以手动进行修改。
5.  **生成并集成：** 点击 “Generate & Integrate” 按钮，创建 `.desktop` 文件，并将您的 AppImage 集成到程序菜单中。

## 依赖

-   Python 3.x
-   `tkinter` (通常随 Python 提供，也可通过系统包管理器安装)
-   `configparser` (Python 标准库)

如果您的系统缺少 `tkinter`，可参考以下命令安装：

### Debian/Ubuntu 系统：

```bash
sudo apt-get install python3 python3-tk
```

## 故障排除

-   如果“Extract & Populate”功能无法找到 `.desktop` 文件或图标，可能是因为 AppImage 的内部结构非常见或缺少相关信息。您仍然可以手动填写所有字段。
-   如果应用没有立即出现在启动器中，请尝试注销后重新登录，或重启桌面环境。有时，从终端手动运行 `update-desktop-database ~/.local/share/applications/` 也能解决问题（本程序会自动尝试执行此命令）。