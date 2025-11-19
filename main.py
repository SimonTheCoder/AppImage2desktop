import os
import shutil
import stat
import subprocess
import tempfile
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
import configparser


class AppImageIntegratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AppImage to Plasma Integrator")
        self.root.geometry(
            "600x450"
        )  # Slightly adjusted height since we are compacting rows

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

    def create_widgets(self):
        # Main Container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky="nsew")

        # Configure column weights for the main frame
        # Column 0: Labels (fixed width mainly)
        # Column 1: Entry fields (expands to fill space)
        # Column 2: Buttons (fixed width)
        main_frame.columnconfigure(1, weight=1)

        # Header
        header = ttk.Label(
            main_frame, text="Integrate AppImage to Desktop", style="Header.TLabel"
        )
        header.grid(row=0, column=0, columnspan=3, pady=(0, 20), sticky="w")

        # Standard padding for rows
        pady_std = 8

        # Row 1: Label | Entry | Button Frame (Browse + Extract & Populate)
        ttk.Label(main_frame, text="AppImage File:").grid(
            row=1, column=0, sticky="w", padx=(0, 10)
        )

        entry_app = ttk.Entry(main_frame, textvariable=self.appimage_path)
        entry_app.grid(row=1, column=1, sticky="ew", pady=pady_std)

        # Button sub-frame for AppImage actions
        app_btn_frame = ttk.Frame(main_frame)
        app_btn_frame.grid(row=1, column=2, padx=(10, 0), pady=pady_std, sticky="e")

        ttk.Button(
            app_btn_frame, text="Browse...", width=8, command=self.browse_appimage
        ).pack(side=tk.LEFT, padx=(0, 2))

        ttk.Button(
            app_btn_frame,
            text="Extract & Populate",
            width=16,
            command=self.extract_and_populate,
        ).pack(side=tk.LEFT)

        # 2. App Name
        # Row 2: Label | Entry (spans 2 cols)
        ttk.Label(main_frame, text="App Name:").grid(
            row=2, column=0, sticky="w", padx=(0, 10)
        )
        ttk.Entry(main_frame, textvariable=self.app_name).grid(
            row=2, column=1, columnspan=2, sticky="ew", pady=pady_std
        )

        # 3. Description / Comment
        # Row 3: Label | Entry (spans 2 cols)
        ttk.Label(main_frame, text="Description:").grid(
            row=3, column=0, sticky="w", padx=(0, 10)
        )
        ttk.Entry(main_frame, textvariable=self.app_comment).grid(
            row=3, column=1, columnspan=2, sticky="ew", pady=pady_std
        )

        # 4. Icon Selection
        # Row 4: Label | Entry | Button Frame (Browse + Extract)
        ttk.Label(main_frame, text="Icon:").grid(
            row=4, column=0, sticky="w", padx=(0, 10)
        )
        ttk.Entry(main_frame, textvariable=self.icon_path).grid(
            row=4, column=1, sticky="ew", pady=pady_std
        )

        # Button sub-frame for Icon actions
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=4, column=2, padx=(10, 0), pady=pady_std, sticky="e")
        ttk.Button(btn_frame, text="Browse", width=8, command=self.browse_icon).pack(
            side=tk.LEFT, padx=(0, 2)
        )

        # 5. Categories
        # Row 5: Label | Combobox (spans 2 cols)
        ttk.Label(main_frame, text="Category:").grid(
            row=5, column=0, sticky="w", padx=(0, 10)
        )
        categories = [
            "Utility",
            "Development",
            "Education",
            "Game",
            "Graphics",
            "Network",
            "Office",
            "AudioVideo",
            "System",
            "Settings",
        ]
        category_cb = ttk.Combobox(
            main_frame,
            textvariable=self.app_category,
            values=categories,
            state="readonly",
        )
        category_cb.grid(row=5, column=1, columnspan=2, sticky="ew", pady=pady_std)

        # 6. Generate Button
        # Row 6: Centered Button
        generate_btn = ttk.Button(
            main_frame, text="Generate & Integrate", command=self.generate_desktop_file
        )
        generate_btn.grid(
            row=6, column=0, columnspan=3, pady=(20, 10), ipady=5, sticky="ew"
        )

        # Status Area
        self.status_label = ttk.Label(
            main_frame, text="Ready", foreground="gray", anchor="center"
        )
        self.status_label.grid(row=7, column=0, columnspan=3, pady=5)

    def browse_appimage(self):
        filename = filedialog.askopenfilename(
            title="Select AppImage",
            filetypes=[("AppImage files", "*.AppImage"), ("All files", "*.*")],
        )
        if filename:
            self.appimage_path.set(filename)
            # Try to guess name
            basename = os.path.basename(filename)
            name_guess = basename.split("-")[0].split("_")[0].capitalize()
            # Remove extension if present (though split above handles typical AppImage naming)
            if name_guess.lower().endswith(".appimage"):
                name_guess = name_guess[:-9]

            if not self.app_name.get():
                self.app_name.set(name_guess)

    def browse_icon(self):
        filename = filedialog.askopenfilename(
            title="Select Icon",
            filetypes=[
                ("Image files", "*.png *.svg *.xpm *.ico *.jpg"),
                ("All files", "*.*"),
            ],
        )
        if filename:
            self.icon_path.set(filename)

    def extract_and_populate(self):
        app_path = self.appimage_path.get()
        if not app_path or not os.path.exists(app_path):
            messagebox.showerror("Error", "Please select a valid AppImage first.")
            return

        self.status_label.config(text="Extracting AppImage...", foreground="blue")
        self.root.update()

        with tempfile.TemporaryDirectory() as temp_dir:
            try:
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
                    messagebox.showwarning(
                        "Not Found", "No .desktop file found in the AppImage."
                    )
                    self.status_label.config(
                        text="Extraction complete, but no .desktop file found.",
                        foreground="orange",
                    )
                    return

                # Parse the .desktop file
                config = configparser.ConfigParser()
                config.read(desktop_file)
                desktop_entry = config["Desktop Entry"]

                self.app_name.set(desktop_entry.get("Name", ""))
                self.app_comment.set(desktop_entry.get("Comment", ""))
                categories = desktop_entry.get("Categories", "Utility").split(";")
                if categories:
                    self.app_category.set(categories[0])

                # Find and copy the icon
                icon_name = desktop_entry.get("Icon")
                if icon_name:
                    icon_path = self.find_icon_file(squashfs_root, icon_name)
                    if icon_path:
                        self.copy_and_set_icon(icon_path)
                    else:
                        messagebox.showwarning(
                            "Icon Not Found",
                            f"Icon '{icon_name}' not found in the AppImage.",
                        )

                self.status_label.config(
                    text="Successfully populated from AppImage.", foreground="green"
                )

            except subprocess.CalledProcessError as e:
                messagebox.showerror(
                    "Extraction Failed",
                    f"Failed to extract AppImage.\n\n{e.stderr.decode()}",
                )
                self.status_label.config(
                    text="AppImage extraction failed.", foreground="red"
                )
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {e}")
                self.status_label.config(text="An error occurred.", foreground="red")

    def find_desktop_file(self, search_dir):
        for root, _, files in os.walk(search_dir):
            for file in files:
                if file.endswith(".desktop"):
                    return os.path.join(root, file)
        return None

    def find_icon_file(self, search_dir, icon_name):
        for root, _, files in os.walk(search_dir):
            for file in files:
                if Path(file).stem == icon_name:
                    return os.path.join(root, file)
        return None

    def copy_and_set_icon(self, icon_path):
        icons_dir = os.path.expanduser("~/.local/share/icons")
        os.makedirs(icons_dir, exist_ok=True)
        
        safe_name = "".join(x for x in self.app_name.get() if x.isalnum()) or "appimage_icon"
        dest_ext = Path(icon_path).suffix
        dest_path = os.path.join(icons_dir, f"{safe_name}{dest_ext}")

        shutil.copy2(icon_path, dest_path)
        self.icon_path.set(dest_path)

    def generate_desktop_file(self):
        # 1. Validation
        app_path = self.appimage_path.get()
        name = self.app_name.get()
        icon = self.icon_path.get()
        category = self.app_category.get()

        if not app_path or not os.path.exists(app_path):
            messagebox.showerror("Error", "AppImage path is invalid.")
            return
        if not name:
            messagebox.showerror("Error", "Application Name is required.")
            return

        # 2. Prepare Paths
        applications_dir = os.path.expanduser("~/.local/share/applications")
        os.makedirs(applications_dir, exist_ok=True)

        desktop_filename = f"{name.replace(' ', '_').lower()}.desktop"
        desktop_path = os.path.join(applications_dir, desktop_filename)

        # 3. Make AppImage Executable
        try:
            st = os.stat(app_path)
            os.chmod(app_path, st.st_mode | stat.S_IEXEC)
        except Exception as e:
            messagebox.showerror("Error", f"Could not make AppImage executable:\n{e}")
            return

        # 4. Generate Content
        # XDG Desktop Entry Specification
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

            # 6. Make .desktop executable (optional but good practice in KDE)
            st = os.stat(desktop_path)
            os.chmod(desktop_path, st.st_mode | stat.S_IEXEC)

            # 7. Trigger Database Update (Helps KDE notice it immediately)
            try:
                subprocess.run(
                    ["update-desktop-database", applications_dir], check=False
                )
            except FileNotFoundError:
                pass  # Tool might not be installed, KDE usually picks it up anyway

            self.status_label.config(
                text=f"Created: {desktop_filename}", foreground="green"
            )
            messagebox.showinfo(
                "Success",
                f"Application added to menu!\n\nFile created at:\n{desktop_path}\n\nYou may need to wait a few seconds for it to appear in the launcher.",
            )

        except Exception as e:
            messagebox.showerror("Error", f"Failed to write desktop file:\n{e}")
            self.status_label.config(text="Write failed.", foreground="red")


if __name__ == "__main__":
    root = tk.Tk()
    app = AppImageIntegratorApp(root)
    root.mainloop()
