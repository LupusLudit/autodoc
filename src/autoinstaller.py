import subprocess
import sys
import importlib

# If AutoInstaller does not work, run these commands in cmd:
# pip install Pillow
# pip install PyPDF2
# pip install reportlab
# pip install customtkinter

class AutoInstaller:
    """
    Class for automatically checking and installing required Python packages.
    """

    REQUIRED_PACKAGES = {
        "Pillow": "PIL",
        "reportlab": "reportlab",
        "PyPDF2": "PyPDF2",
        "customtkinter": "customtkinter"
    }

    @classmethod
    def ensure_packages(cls):
        """
        Class method for ensuring all required packages are installed.
        Checks if each package can be imported; if not, installs it automatically.
        After installation, the script restarts itself.
        :return: Nothing
        """
        missing = []
        for package, import_name in cls.REQUIRED_PACKAGES.items():
            try:
                importlib.import_module(import_name)
            except ImportError:
                print(f"[INFO] Missing package detected: {package}")
                missing.append(package)

        if missing:
            print("[INFO] Installing missing packages...")
            for package in missing:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])

            print("[INFO] Restarting script after installation...")
            # Restart script
            subprocess.Popen([sys.executable] + sys.argv)
            sys.exit()  # Exit the current instance to avoid running twice
