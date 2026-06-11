"""Create a desktop shortcut for AppImage Integrator itself."""

import os
from pathlib import Path


def create_desktop_shortcut():
    """Create a .desktop file to launch AppImage Integrator from the system menu."""
    # Determine icon path - use bundled icon.png if it exists, otherwise use default
    current_dir = Path(__file__).parent.parent  # project root
    icon_path = current_dir / "icon.png"

    if icon_path.exists():
        icon_file = str(icon_path)
    else:
        icon_file = "application-x-executable"

    # Create desktop file content
    desktop_content = f"""[Desktop Entry]
Name=AppImage Integrator
Comment=Integrate AppImages into KDE Plasma desktop
Exec=appimage2desktop
Icon={icon_file}
Terminal=false
Type=Application
Categories=Utility;KDE;
"""

    # Create the target directory if it doesn't exist
    target_dir = Path.home() / ".local/share/applications"
    target_dir.mkdir(parents=True, exist_ok=True)

    # Write the desktop file to the standard location
    desktop_file_path = target_dir / "appimage-integrator.desktop"
    try:
        with open(desktop_file_path, "w") as f:
            f.write(desktop_content)

        # Make it executable
        os.chmod(desktop_file_path, 0o755)

        print(f"Desktop shortcut created successfully at {desktop_file_path}")
        print("You can now find 'AppImage Integrator' in your KDE applications menu.")
        return True

    except Exception as e:
        print(f"Error creating desktop shortcut: {e}")
        return False


if __name__ == "__main__":
    create_desktop_shortcut()
