"""Create a desktop shortcut for AppImage2desktop itself."""

import os
import shutil
import subprocess
import sys
from pathlib import Path


def _resolve_exec() -> str:
    """Resolve how to launch this tool from a .desktop file.

    Prefers the installed console script; falls back to running the
    package as a module with the current interpreter."""
    console_script = shutil.which("appimage2desktop")
    if console_script:
        return f'"{console_script}"'
    return f'"{sys.executable}" -m appimage2desktop'


def _resolve_icon() -> str:
    """Find the bundled icon, falling back to a theme icon."""
    candidates = [
        Path(__file__).parent / "icon.png",      # installed alongside package
        Path(__file__).parent.parent / "icon.png",  # project root (dev/editable)
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    return "application-x-executable"


def create_desktop_shortcut() -> Path:
    """Create a .desktop file to launch AppImage2desktop from the system menu.

    Returns the path of the created desktop file. Raises on failure."""
    target_dir = Path.home() / ".local/share/applications"
    target_dir.mkdir(parents=True, exist_ok=True)

    desktop_content = f"""[Desktop Entry]
Name=AppImage2desktop
Comment=Integrate AppImages into KDE Plasma desktop
Exec={_resolve_exec()}
Icon={_resolve_icon()}
Terminal=false
Type=Application
Categories=Utility;KDE;
"""

    desktop_file_path = target_dir / "appimage-integrator.desktop"
    with open(desktop_file_path, "w") as f:
        f.write(desktop_content)

    # Make it executable so the launcher treats it as trusted
    os.chmod(desktop_file_path, 0o755)

    # Trigger desktop database update so the entry appears promptly
    try:
        subprocess.run(["update-desktop-database", str(target_dir)], check=False)
    except FileNotFoundError:
        pass

    return desktop_file_path


if __name__ == "__main__":
    path = create_desktop_shortcut()
    print(f"Desktop shortcut created successfully at {path}")
    print("You can now find 'AppImage2desktop' in your KDE applications menu.")
