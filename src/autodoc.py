from autoinstaller import AutoInstaller
AutoInstaller.ensure_packages()

from customtkinter import *
from screenshotapp import ScreenshotApp

# Note 1: The pdf file cannot be opened in another program while using autodoc
# Note 2: Run the code via the bat file, otherwise there might be problem with some of the filepaths
    
if __name__ == "__main__":
    root = CTk()
    set_default_color_theme("blue")
    set_appearance_mode("Dark") 
    app = ScreenshotApp(root)
    root.mainloop()
