import os
from customtkinter import *
from PIL import Image

class SettingsMenu:
    def __init__(self, root, assets_path):
        self.root = root
        self.assets_path = assets_path
        self.is_visible = False

        # Variables
        self.auto_popUp = BooleanVar(value=True)
        self.auto_minimalize = BooleanVar(value=False)

        # Icon
        dark_icon_path = os.path.join(self.assets_path, "settingsImageBlack.png")
        light_icon_path = os.path.join(self.assets_path, "settingsImageGrey.png")
        self.settings_icon_light = CTkImage(light_image=Image.open(dark_icon_path), size=(25, 25))
        self.settings_icon_dark = CTkImage(light_image=Image.open(light_icon_path), size=(25, 25))

        # Frame for button
        self.settings_frame = CTkFrame(root, width=40, height=40, fg_color="transparent")
        self.settings_frame.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=10)

        # Settings button
        self.settings_button = CTkButton(self.settings_frame, image=self.get_icon(),
                                        text="", width=30, height=30,
                                        command=self.toggle_menu, fg_color="transparent", hover=False)
        self.settings_button.pack()

        # Menu
        self.settings_menu = CTkFrame(root, width=250, height=0)
        self.settings_menu.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=60)
        self.settings_menu.grid_propagate(False)

        self.theme_switch = CTkSwitch(self.settings_menu, text="Dark Mode", command=self.toggle_theme)
        self.theme_switch.grid(row=0, column=0, pady=10, padx=10, sticky="w")

        self.auto_popUp_checkbox = CTkCheckBox(self.settings_menu, text="Automatic window pop up",
                                               variable=self.auto_popUp)
        self.auto_popUp_checkbox.grid(row=1, column=0, pady=10, padx=10, sticky="w")

        self.auto_minimalize_checkbox = CTkCheckBox(self.settings_menu, text="Automatic window minimalization",
                                                    variable=self.auto_minimalize)
        self.auto_minimalize_checkbox.grid(row=2, column=0, pady=10, padx=10, sticky="w")

        self.initialize_theme()

    def get_icon(self):
        """Retrun which icon should be used."""
        if get_appearance_mode() == "Dark":
            return self.settings_icon_dark
        else:
            return self.settings_icon_light

    def toggle_theme(self):
        """Toggle between dark and light mode."""
        set_appearance_mode("Light" if get_appearance_mode() == "Dark" else "Dark")
        self.settings_button.configure(image=self.get_icon())

    def toggle_menu(self):
        """Toggle menu visibility."""
        if self.is_visible:
            self.animate(opening=False)
        else:
            self.settings_menu.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=60)
            self.animate(opening=True)

    def animate(self, opening):
        """Animate window closing/opening."""
        target_height = 150 if opening else 0
        step = 5 if opening else -5
        current_height = self.settings_menu.winfo_height()

        def animate_step():
            nonlocal current_height
            current_height += step
            if (opening and current_height >= target_height) or (not opening and current_height <= target_height):
                self.settings_menu.configure(height=target_height)
                self.is_visible = opening
                return
            self.settings_menu.configure(height=current_height)
            self.root.after(5, animate_step)

        animate_step()

    def initialize_theme(self):
        """Initialize theme based on system settings."""
        set_appearance_mode("Dark")
        self.theme_switch.select()
        self.settings_button.configure(image=self.get_icon())
