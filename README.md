# AppImage2Desktop

## AppImage to Plasma Integrator

This application provides a graphical user interface (GUI) to easily integrate AppImage applications into your Plasma (KDE) desktop environment. It allows you to create `.desktop` files, making your AppImage applications appear in your application launcher with proper names, descriptions, and icons.

## Features

- **AppImage Selection:** Browse and select your AppImage file.
- **Extract & Populate:** Automatically extracts information (Name, Comment, Icon, Categories) from the selected AppImage's internal `.desktop` file and populates the UI fields. This streamlines the integration process significantly.
- **Customization:** Manually adjust the application name, description, icon path, and category if needed.
- **Icon Extraction:** If an icon is specified in the AppImage's internal `.desktop` file, it will be extracted and saved to `~/.local/share/icons/`.
- **Desktop File Generation:** Creates a `.desktop` file in `~/.local/share/applications/` for seamless integration with your desktop environment.
- **Executable Permissions:** Automatically sets executable permissions for both the AppImage and the generated `.desktop` file.

## How to Use

1.  **Run the Application:**
    ```bash
    python3 main.py
    ```
2.  **Select AppImage:** Click the "Browse..." button next to "AppImage File:" and select your desired AppImage.
3.  **Extract & Populate (Recommended):** Click the "Extract & Populate" button. This will:
    *   Extract the contents of the AppImage to a temporary location.
    *   Search for a `.desktop` file within the extracted content.
    *   If found, it will read the application's Name, Comment, and Icon information and automatically fill in the corresponding fields in the GUI.
    *   It will also attempt to extract and save the specified icon to `~/.local/share/icons/` and update the "Icon" field.
4.  **Review/Customize:** Verify the "App Name," "Description," "Icon," and "Category" fields. You can adjust them manually if the extracted information isn't perfect or if you wish to use a different icon (via the "Browse" button next to "Icon").
5.  **Generate & Integrate:** Click the "Generate & Integrate" button. This will create the `.desktop` file and integrate your AppImage into your application menu.

## Prerequisites

-   Python 3.x
-   `tkinter` (usually included with Python or available via your system's package manager)
-   `configparser` (standard Python library)

## Installation of Dependencies (if needed)

### Debian/Ubuntu-based Systems:

```bash
sudo apt-get install python3 python3-tk
```

## Troubleshooting

-   If the "Extract & Populate" feature doesn't find a `.desktop` file or icon, the AppImage might be structured differently than expected, or the information might be missing. You can still fill in the details manually.
-   If the application doesn't appear in your launcher immediately, try logging out and back in, or restarting your desktop environment. Sometimes running `update-desktop-database ~/.local/share/applications/` manually from a terminal can help, but the application attempts to do this automatically.