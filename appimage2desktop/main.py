"""AppImage to Plasma Desktop Integrator - GUI Application."""

import os
import shutil
import stat
import subprocess
import tempfile
import threading
import configparser
from pathlib import Path
from typing import Optional
from tkinter import filedialog, messagebox, ttk
import tkinter as tk


class AppImageIntegratorApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("AppImage to Plasma Integrator")
        self.root.geometry("600x450")

        # Configure root grid expansion
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Styles
        style = ttk.Style()
        style.configure("TButton", font=("Helvetica", 9))
        style.configure("TLabel", font=("Helvetica", 10))
        style.configure("Header.TLabel", font=("Helvetica", 12, "bold"))

        # Variables
        self.appimage_path = tk.StringVar()
        self.app_name = tk.StringVar()
        self.app_comment = tk.StringVar(value="AppImage Application")
        self.icon_path = tk.StringVar()
        self.app_category = tk.StringVar(value="Utility")

        # Layout
        self.create_widgets()

    def create_widgets(self) -> None:
        # Main Container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky="nsew")

        # Configure column weights
        main_frame.columnconfigure(1, weight=1)

        # Header
        header = ttk.Label(
            main_frame, text="Integrate AppImage to Desktop", style="Header.TLabel"
        )
        header.grid(row=0, column=0, columnspan=3, pady=(0, 20), sticky="w")

        pady_std = 8

        # Row 1: AppImage File
        ttk.Label(main_frame, text="AppImage File:").grid(
            row=1, column=0, sticky="w", padx=(0, 10)
        )

        entry_app = ttk.Entry(main_frame, textvariable=self.appimage_path)
        entry_app.grid(row=1, column=1, sticky="ew", pady=pady_std)

        app_btn_frame = ttk.Frame(main_frame)
        app_btn_frame.grid(row=1, column=2, padx=(10, 0), pady=pady_std, sticky="e")

        ttk.Button(
            app_btn_frame, text="Browse...", width=8, command=self.browse_appimage
        ).pack(side=tk.LEFT, padx=(0, 2))

        ttk.Button(
            app_btn_frame,
            text="Extract & Populate",
            width=16,
            command=self.extract_and_populate_async,
        ).pack(side=tk.LEFT)

        # Row 2: App Name
        ttk.Label(main_frame, text="App Name:").grid(
            row=2, column=0, sticky="w", padx=(0, 10)
        )
        ttk.Entry(main_frame, textvariable=self.app_name).grid(
            row=2, column=1, columnspan=2, sticky="ew", pady=pady_std
        )

        # Row 3: Description
        ttk.Label(main_frame, text="Description:").grid(
            row=3, column=0, sticky="w", padx=(0, 10)
        )
        ttk.Entry(main_frame, textvariable=self.app_comment).grid(
            row=3, column=1, columnspan=2, sticky="ew", pady=pady_std
        )

        # Row 4: Icon Selection
        ttk.Label(main_frame, text="Icon:").grid(
            row=4, column=0, sticky="w", padx=(0, 10)
        )
        ttk.Entry(main_frame, textvariable=self.icon_path).grid(
            row=4, column=1, sticky="ew", pady=pady_std
        )

        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=4, column=2, padx=(10, 0), pady=pady_std, sticky="e")
        ttk.Button(btn_frame, text="Browse", width=8, command=self.browse_icon).pack(
            side=tk.LEFT, padx=(0, 2)
        )

        # Row 5: Categories
        ttk.Label(main_frame, text="Category:").grid(
            row=5, column=0, sticky="w", padx=(0, 10)
        )
        categories = [
            "Utility", "Development", "Education", "Game", "Graphics",
            "Network", "Office", "AudioVideo", "System", "Settings",
        ]
        category_cb = ttk.Combobox(
            main_frame,
            textvariable=self.app_category,
            values=categories,
            state="readonly",
        )
        category_cb.grid(row=5, column=1, columnspan=2, sticky="ew", pady=pady_std)

        # Row 6: Generate Button
        generate_btn = ttk.Button(
            main_frame, text="Generate & Integrate", command=self.generate_desktop_file_async
        )
        generate_btn.grid(
            row=6, column=0, columnspan=3, pady=(20, 10), ipady=5, sticky="ew"
        )

        # Status Area
        self.status_label = ttk.Label(
            main_frame, text="Ready", foreground="gray", anchor="center"
        )
        self.status_label.grid(row=7, column=0, columnspan=3, pady=5)

    def _update_ui_status(self, text: str, color: str = "black") -> None:
        """Thread-safe way to update the status label."""
        self.root.after(0, lambda: self.status_label.config(text=text, foreground=color))

    def _show_error_dialog(self, title: str, message: str) -> None:
        """Thread-safe way to show error dialogs."""
        self.root.after(0, lambda: messagebox.showerror(title, message))

    def _show_info_dialog(self, title: str, message: str) -> None:
        """Thread-safe way to show info dialogs."""
        self.root.after(0, lambda: messagebox.showinfo(title, message))

    def _show_warning_dialog(self, title: str, message: str) -> None:
        """Thread-safe way to show warning dialogs."""
        self.root.after(0, lambda: messagebox.showwarning(title, message))

    def _confirm_permission_change(self, app_path: str) -> bool:
        """Show a confirmation dialog before making the AppImage executable.
        Thread-safe: works from both main and worker threads.
        Skips the prompt if the file is already executable."""
        st = os.stat(app_path)
        if st.st_mode & stat.S_IEXEC:
            return True

        result = [False]
        ready = threading.Event()

        def show_dialog():
            answer = messagebox.askyesno(
                "Security Warning",
                f"This action will make the following file executable:\n\n{app_path}\n\nDo you want to proceed?",
            )
            result[0] = answer
            ready.set()

        self.root.after(0, show_dialog)
        ready.wait()
        return result[0]

    def browse_appimage(self) -> None:
        filename = filedialog.askopenfilename(
            title="Select AppImage",
            filetypes=[("AppImage files", ("*.AppImage", "*.appimage")), ("All files", "*.*")],
        )
        if filename:
            self.appimage_path.set(filename)
            basename = os.path.basename(filename)
            name_guess = basename.split("-")[0].split("_")[0].capitalize()
            if name_guess.lower().endswith(".appimage"):
                name_guess = name_guess[:-9]

            if not self.app_name.get():
                self.app_name.set(name_guess)

    def browse_icon(self) -> None:
        filename = filedialog.askopenfilename(
            title="Select Icon",
            filetypes=[
                ("Image files", "*.png *.svg *.xpm *.ico *.jpg"),
                ("All files", "*.*"),
            ],
        )
        if filename:
            self.icon_path.set(filename)

    def extract_and_populate_async(self) -> None:
        """Triggered by the button. Starts the extraction thread."""
        app_path = self.appimage_path.get()
        if not app_path or not os.path.exists(app_path):
            self._show_error_dialog("Error", "Please select a valid AppImage first.")
            return

        threading.Thread(target=self._threaded_extract_and_populate, args=(app_path,), daemon=True).start()

    def _threaded_extract_and_populate(self, app_path: str) -> None:
        """The actual heavy lifting in a background thread."""
        self._update_ui_status("Extracting AppImage...", "blue")

        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                # Security: confirm before changing executable permission
                if not self._confirm_permission_change(app_path):
                    self._update_ui_status("Extraction cancelled by user.", "orange")
                    return

                st = os.stat(app_path)
                os.chmod(app_path, st.st_mode | stat.S_IEXEC)

                # Extract the AppImage
                subprocess.run(
                    [app_path, "--appimage-extract"],
                    cwd=temp_dir,
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                squashfs_root = os.path.join(temp_dir, "squashfs-root")

                # Find the .desktop file
                desktop_file = self.find_desktop_file(squashfs_root)
                if not desktop_file:
                    self._show_warning_dialog("Not Found", "No .desktop file found in the AppImage.")
                    self._update_ui_status("Extraction complete, but no .desktop file found.", "orange")
                    return

                # Parse the .desktop file
                config = configparser.ConfigParser()
                config.read(desktop_file)
                desktop_entry = config["Desktop Entry"]

                # Update UI variables via thread-safe method
                self.root.after(0, lambda: self.app_name.set(desktop_entry.get("Name", "")))
                self.root.after(0, lambda: self.app_comment.set(desktop_entry.get("Comment", "")))
                categories = desktop_entry.get("Categories", "Utility").split(";")
                if categories:
                    self.root.after(0, lambda: self.app_category.set(categories[0]))

                # Find and copy the icon
                icon_name = desktop_entry.get("Icon")
                if icon_name:
                    icon_path = self.find_icon_file(squashfs_root, icon_name)
                    if icon_path:
                        self.copy_and_set_icon(icon_path)
                    else:
                        self._show_warning_dialog(
                            "Icon Not Found",
                            f"Icon '{icon_name}' not found in the AppImage.",
                        )

                self._update_ui_status("Successfully populated from AppImage.", "green")

            except subprocess.CalledProcessError as e:
                err_msg = e.stderr.decode() if e.stderr else str(e)
                self._show_error_dialog("Extraction Failed", f"Failed to extract AppImage.\n\n{err_msg}")
                self._update_ui_status("AppImage extraction failed.", "red")
            except Exception as e:
                self._show_error_dialog("Error", f"An error occurred: {e}")
                self._update_ui_status("An error occurred.", "red")

    def find_desktop_file(self, search_dir: str) -> Optional[str]:
        for root, _, files in os.walk(search_dir):
            for file in files:
                if file.endswith(".desktop"):
                    return os.path.join(root, file)
        return None

    def find_icon_file(self, search_dir: str, icon_name: str) -> Optional[str]:
        for root, _, files in os.walk(search_dir):
            for file in files:
                if Path(file).stem == icon_name:
                    return os.path.join(root, file)
        return None

    def copy_and_set_icon(self, icon_path: str) -> None:
        icons_dir = os.path.expanduser("~/.local/share/icons")
        os.makedirs(icons_dir, exist_ok=True)
        
        safe_name = "".join(x for x in self.app_name.get() if x.isalnum()) or "appimage_icon"
        dest_ext = Path(icon_path).suffix
        dest_path = os.path.join(icons_dir, f"{safe_name}{dest_ext}")

        shutil.copy2(icon_path, dest_path)
        self.icon_path.set(dest_path)

    def generate_desktop_file_async(self) -> None:
        """Triggered by the button. Starts the generation thread."""
        app_path = self.appimage_path.get()
        name = self.app_name.get()
        icon = self.icon_path.get()
        category = self.app_category.get()

        if not app_path or not os.path.exists(app_path):
            self._show_error_dialog("Error", "AppImage path is invalid.")
            return
        if not name:
            self._show_error_dialog("Error", "Application Name is required.")
            return

        self._update_ui_status("Generating file...", "blue")
        threading.Thread(target=self._threaded_generate_desktop_file, args=(app_path, name, icon, category), daemon=True).start()

    def _threaded_generate_desktop_file(self, app_path: str, name: str, icon: str, category: str) -> None:
        """The actual heavy lifting in a background thread."""
        applications_dir = os.path.expanduser("~/.local/share/applications")
        os.makedirs(applications_dir, exist_ok=True)

        desktop_filename = f"{name.replace(' ', '_').lower()}.desktop"
        desktop_path = os.path.join(applications_dir, desktop_filename)

        # 3. Security: confirm before making AppImage executable
        if not self._confirm_permission_change(app_path):
            self._update_ui_status("Generation cancelled by user.", "orange")
            return

        try:
            st = os.stat(app_path)
            os.chmod(app_path, st.st_mode | stat.S_IEXEC)
        except Exception as e:
            self._show_error_dialog("Error", f"Could not make AppImage executable:\n{e}")
            self._update_ui_status("Error making AppImage executable.", "red")
            return

        # 4. Generate Content
        content = [
            "[Desktop Entry]",
            "Type=Application",
            f"Name={name}",
            f"Comment={self.app_comment.get()}",
            f'Exec="{app_path}"',
            f"Categories={category};",
            "Terminal=false",
        ]

        if icon:
            content.append(f"Icon={icon}")

        # 5. Write File
        try:
            with open(desktop_path, "w") as f:
                f.write("\n".join(content))

            # 6. Make .desktop executable
            st = os.stat(desktop_path)
            os.chmod(desktop_path, st.st_mode | stat.S_IEXEC)

            # 7. Trigger Database Update
            try:
                subprocess.run(
                    ["update-desktop-database", applications_dir], check=False
                )
            except FileNotFoundError:
                pass

            self._update_ui_status(f"Created: {desktop_filename}", "green")
            self._show_info_dialog(
                "Success",
                f"Application added to menu!\n\nFile created at:\n{desktop_path}\n\nYou may need to wait a few seconds for it to appear in the launcher.",
            )

        except Exception as e:
            self._show_error_dialog("Error", f"Failed to write desktop file:\n{e}")
            self._update_ui_status("Write failed.", "red")


def main() -> None:
    """Entry point for the GUI application."""
    root = tk.Tk()
    app = AppImageIntegratorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
