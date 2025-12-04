#!/usr/bin/env python3
import os
import sys
from pathlib import Path


def create_desktop_shortcut():
    # Get the directory where main.py is located
    current_dir = Path(__file__).parent.absolute()
    main_py_path = current_dir / "main.py"

    # Check if main.py exists
    if not main_py_path.exists():
        print(f"Error: main.py not found at {main_py_path}")
        return False

    # Create desktop file content
    desktop_content = f"""[Desktop Entry]
Name=AppImage Integrator
Comment=Integrate AppImages into KDE Plasma desktop
Exec=python3 "{main_py_path}"
Icon=application-x-executable
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
