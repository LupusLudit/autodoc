import subprocess
import sys
import importlib

class AutoInstaller:
    REQUIRED_PACKAGES = {
        "Pillow": "PIL",
        "reportlab": "reportlab",
        "PyPDF2": "PyPDF2",
        "customtkinter": "customtkinter"
    }

    @classmethod
    def ensure_packages(cls):
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

# Run the installer
AutoInstaller.ensure_packages()


import os
from datetime import datetime
from PIL import ImageGrab, ImageTk
from customtkinter import*
from tkinter import filedialog, messagebox
import json
import hashlib
from reportlab.pdfgen import canvas 
from reportlab.pdfbase.ttfonts import TTFont 
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.pagesizes import letter
from PIL import Image
from PyPDF2 import PdfReader, PdfWriter
from datetime import datetime

#If AutoInstaller doesnt work install these packages
#pip install PyPDF2
#pip install reportlab

#Note: The pdf file cannot be opened in another program while using autodoc
#TODO: Clean the code, change main icon

class ScreenshotApp():
    def __init__(self, root):
        self.root = root
        self.root.title("Auto Screenshot Documenter")
        self.root.geometry("1024x950")

        # Variables for paths
        self.screenshot_dir = None
        self.doc_path = None
        self.current_class = None
        self.current_screenshot = None
        self.screenshot_preview = None
        self.previous_image = None
        self.doc = None

        # Mode Selection (Existing file or New file)
        self.mode_var = StringVar(value="new")  # Default: create new file
        self.use_default_dir = BooleanVar(value=False)
        self.use_default_class = BooleanVar(value=False)

        self.default_screenshot_dir = os.path.join(os.getcwd(), "img")
        self.default_class = "C3a"
        print(f"Default screenshot directory: {self.default_screenshot_dir}")

        CTkLabel(root, text="Choose Mode:").pack(pady=5)
        CTkRadioButton(root, text="Create New PDF", variable=self.mode_var, value="new", command=self.toggle_mode).pack()
        CTkRadioButton(root, text="Open Existing PDF", variable=self.mode_var, value="existing", command=self.toggle_mode).pack()

        CTkCheckBox(root, text="Use default screenshot directory",
                     variable=self.use_default_dir, onvalue=True, offvalue=False,
                     command=self.toggle_default_dir).pack()

        # UI Elements for path selection
        CTkLabel(root, text="Select Screenshot Directory:").pack(pady=5)
        self.screenshot_entry = CTkEntry(root, width=500)
        self.screenshot_entry.pack(pady=5)
        self.screenshot_entry.bind("<KeyRelease>", lambda e: self.update_screenshot_dir())
        self.screenshot_browse_button = CTkButton(root, text="Browse", command=self.set_screenshot_dir, corner_radius=15)
        self.screenshot_browse_button.pack()


        CTkLabel(root, text="Select Document File:").pack(pady=5)
        self.doc_entry = CTkEntry(root, width=500)
        self.doc_entry.pack(pady=5)
        self.doc_entry.bind("<KeyRelease>", lambda e: self.update_doc_path())
        CTkButton(root, text="Browse", command=self.browse_doc, corner_radius=15).pack()

        # Metadata fields (Only shown for new PDFs)
        self.metadata_frame = CTkFrame(root)
        self.metadata_frame.pack(pady=10)

        CTkLabel(self.metadata_frame, text="Enter new file name:").pack(pady=5)
        self.fileName_entry = CTkEntry(self.metadata_frame, width=300)
        self.fileName_entry.pack(pady=5)
        self.fileName_entry.bind("<KeyRelease>", lambda e: self.update_doc_path())
        self.fileName_entry.configure(placeholder_text="CVnumber_Surname_ExerciseTitle")

        # Validation for numeric-only entry
        vcmd = root.register(self.validate_numeric_input)

        CTkLabel(self.metadata_frame, text="Enter Exercise number:").pack(pady=5)
        self.exercise_entry = CTkEntry(self.metadata_frame, width=150,
                                       validate="key", 
                                       validatecommand=(vcmd, '%P'))
        self.exercise_entry.pack(pady=5)
        self.exercise_entry.configure(placeholder_text="01")


        CTkLabel(self.metadata_frame, text="Enter Main Title:").pack(pady=5)
        self.title_entry = CTkEntry(self.metadata_frame, width=300)
        self.title_entry.pack(pady=5)
        self.title_entry.configure(placeholder_text="W2012Srv_IIS")

        CTkLabel(self.metadata_frame, text="Enter your name:").pack(pady=5)
        self.name_entry = CTkEntry(self.metadata_frame, width=300)
        self.name_entry.pack(pady=5)
        self.name_entry.configure(placeholder_text="George")

        CTkLabel(self.metadata_frame, text="Enter your surname:").pack(pady=5)
        self.surname_entry = CTkEntry(self.metadata_frame, width=300)
        self.surname_entry.pack(pady=5)
        self.surname_entry.configure(placeholder_text="Orwell")

        CTkCheckBox(self.metadata_frame, text="Use default class",
                    variable=self.use_default_class, onvalue=True, offvalue=False,
                    command=self.toggle_default_class).pack()

        CTkLabel(self.metadata_frame, text="Enter your Class:").pack(pady=5)
        self.class_entry = CTkEntry(self.metadata_frame, width=300)
        self.class_entry.bind("<KeyRelease>", lambda e: self.update_class())
        self.class_entry.pack(pady=5)
        self.class_entry.configure(placeholder_text="C3a")
        
        self.prompt_mode_var = StringVar(value="regular")

        CTkLabel(self.metadata_frame, text="Choose prompt mode:").pack(pady=5)
        CTkRadioButton(self.metadata_frame, text="Regular prompts (no numbering)", variable=self.prompt_mode_var, value="regular").pack()
        CTkRadioButton(self.metadata_frame, text="Automatic prompt numbering", variable=self.prompt_mode_var, value="numbered").pack()

        # OK Button
        self.ok_button = CTkButton(root, text="OK", command=self.start_monitoring,
                                fg_color="lime green", text_color="black", 
                                corner_radius=20, border_width=2, border_color="green",
                                hover_color="#90ee90")
        self.ok_button.place(relx=0.5, rely=1.0, anchor="s", y=-10)  # Centered at the bottom

        # Close Button
        CTkButton(root, text="CLOSE", command=root.quit,
                fg_color="red", text_color="white",
                corner_radius=20, border_width=2, border_color="dark red",
                hover_color="#ff6666").place(relx=1.0, rely=1.0, x=-10, y=-10, anchor="se")

        self.image_label = CTkLabel(root, text="")  
        self.image_label.pack(pady=10)
        self.image_label.pack_forget()

        # Settings
        self.is_settings_menu_visible = False

        assets_path = os.path.join(os.getcwd(), "assets")

        dark_icon_path = os.path.join(assets_path, "settingsImageBlack.png")
        light_icon_path = os.path.join(assets_path, "settingsImageGrey.png")
        self.auto_popUp = BooleanVar(value=True)
        self.auto_minimalize = BooleanVar(value=False)

        self.settings_icon_light = CTkImage(light_image=Image.open(dark_icon_path), size=(25, 25))
        self.settings_icon_dark = CTkImage(light_image=Image.open(light_icon_path), size=(25, 25))

        self.settings_frame = CTkFrame(root, width=40, height=40, fg_color="transparent")
        self.settings_frame.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=10)

        self.settings_button = CTkButton(self.settings_frame, image=self.get_correct_settings_icon(),
                                        text="", width=30, height=30,
                                        command=self.toggle_settings_menu, fg_color="transparent", hover=False)
        self.settings_button.pack()

        self.settings_menu = CTkFrame(root, width=200, height=0)
        self.settings_menu.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=60)
        self.settings_menu.grid_propagate(False)  # Prevent auto resizing

        self.theme_switch = CTkSwitch(self.settings_menu, text="Dark Mode", command=self.toggle_theme)
        self.theme_switch.grid(row=0, column=0, pady=10, padx=10, sticky="w")
        self.auto_popUp_checkbox = CTkCheckBox(self.settings_menu, text="Auto pop up",
                    variable=self.auto_popUp, onvalue=True, offvalue=False,)
        self.auto_popUp_checkbox.grid(row=1, column=0, pady=10, padx=10, sticky="w")
        self.auto_minimalize_checkbox = CTkCheckBox(self.settings_menu, text="Auto minimalize",
                    variable=self.auto_minimalize, onvalue=True, offvalue=False,)
        self.auto_minimalize_checkbox.grid(row=2, column=0, pady=10, padx=10, sticky="w")
        self.initialize_theme()

        # Screenshot Description (Initially Hidden)
        self.prompt_entry = CTkTextbox(root, width=600, height=200, wrap="word")
        self.prompt_entry.pack(pady=5)
        self.prompt_entry.insert("1.0", "Here enter the screenshot description")
        self.prompt_entry.pack(pady=10)
        self.prompt_entry.pack_forget()

        # Save and Discard Buttons (Initially Hidden)
        self.save_button = CTkButton(root, text="SAVE", command=self.save_screenshot,
                            fg_color="lime green", text_color="black", 
                            corner_radius=20, border_width=2, border_color="green",
                            hover_color="#90ee90")
        self.save_button.pack(pady=10)
        self.save_button.pack_forget()

        self.discard_button = CTkButton(root, text="DISCARD", command=self.discard_screenshot,
                                fg_color="red", text_color="white",
                                corner_radius=20, border_width=2, border_color="dark red",
                                hover_color="#ff6666")
        self.discard_button.pack(pady=10)
        self.discard_button.pack_forget()

        self.toggle_mode()  # Initialize correct visibility

    def initialize_theme(self):
        """Initialize theme based on system settings."""
        mode = "Dark"
        set_appearance_mode(mode)
        self.theme_switch.select() if mode == "Dark" else self.theme_switch.deselect()
        self.settings_button.configure(image=self.get_correct_settings_icon())


    def get_correct_settings_icon(self):
        """Return the correct settings icon based on system settings."""
        if get_appearance_mode() == "Dark":
            return self.settings_icon_dark
        else:
            return self.settings_icon_light

    def toggle_theme(self):
        """Toggle between dark and light mode."""
        if get_appearance_mode() == "Dark":
            set_appearance_mode("Light")
        else:
            set_appearance_mode("Dark")
        
        self.settings_button.configure(image=self.get_correct_settings_icon())

    def toggle_settings_menu(self):
        """Show/hide the settings dropdown with animation."""
        if self.is_settings_menu_visible:
            self.animate_settings_menu(opening=False)
        else:
            self.settings_menu.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=60)
            self.animate_settings_menu(opening=True)
        
        self.is_settings_menu_visible = not self.is_settings_menu_visible

    def animate_settings_menu(self, opening=True):
        """Animate the settings dropdown menu."""
        max_height = 150
        step = 10
        current_height = self.settings_menu.winfo_height()

        def expand():
            nonlocal current_height
            if current_height < max_height:
                current_height += step
                self.settings_menu.configure(height=current_height)
                self.root.after(10, expand)

        def collapse():
            nonlocal current_height
            if current_height > 0:
                current_height -= step
                self.settings_menu.configure(height=current_height)
                self.root.after(10, collapse)
            else:
                self.settings_menu.place_forget()

        expand() if opening else collapse()

    def validate_numeric_input(self, value):
        """Make sure the the input is numeric or empty."""
        return value.isdigit() or value == ""
    
    def raise_above_all(self):
        """Raise the window above all other windows."""
        if self.root.state() == 'iconic':
            self.root.deiconify()

        self.root.lift()
        self.root.attributes('-topmost', 1)
        self.root.attributes('-topmost', 0)

    def minimalize(self):
        """Minimize the window."""
        self.root.iconify()


    def toggle_mode(self):
        """Show or hide metadata fields based on selected mode."""
        self.screenshot_entry.configure(placeholder_text="path/to/screenshot/directory")
        if self.mode_var.get() == "new":
            self.metadata_frame.pack(pady=10)
            self.doc_entry.configure(placeholder_text="path/to/the/new/PDF/file")
        else:
            self.metadata_frame.pack_forget()
            self.doc_entry.configure(placeholder_text="path/to/the/existing/PDF/file")

    def toggle_default_dir(self):
        """Toggle default directory selection."""
        if self.use_default_dir.get():
            self.screenshot_entry.delete(0, "end")
            self.screenshot_dir = self.default_screenshot_dir
            self.screenshot_entry.insert(0, self.default_screenshot_dir)
            self.screenshot_entry.configure(state="disabled")
            self.screenshot_browse_button.configure(state="disabled")
        else:
            self.screenshot_entry.configure(state="normal")
            self.screenshot_entry.delete(0, "end")
            self.screenshot_entry.configure(placeholder_text="path/to/screenshot/directory")
            self.screenshot_browse_button.configure(state="normal")
            self.toggle_mode()

    def toggle_default_class(self):
        """Toggle default class selection."""
        if self.use_default_class.get():
            self.class_entry.delete(0, "end")
            self.class_entry.insert(0, self.default_class)
            self.class_entry.configure(state="disabled")
        else:
            self.class_entry.configure(state="normal")
            self.class_entry.delete(0, "end")
            self.class_entry.configure(placeholder_text="C3a")


    def set_screenshot_dir(self):
        """Set the directory where screenshots will be saved."""
        directory = filedialog.askdirectory()
        if directory:
            self.screenshot_dir = directory
            self.screenshot_entry.delete(0, "end")
            self.screenshot_entry.insert(0, directory)

    def browse_doc(self):
        """Set the PDF file path based on selected mode."""
        if self.mode_var.get() == "new":
            file_path = filedialog.askdirectory()
            if file_path:
                if self.fileName_entry.get():
                    self.doc_path = os.path.join(file_path, f"{self.fileName_entry.get()}.pdf")
                else:
                    self.doc_path = os.path.join(file_path, "new_autodoc_file.pdf")
                self.doc_entry.delete(0, "end")
                self.doc_entry.insert(0, file_path)
        else:
            file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
            if file_path:
                # Check if the selected file exists
                if not os.path.isfile(file_path):
                    messagebox.showerror("Error", "The selected file path is invalid or does not exist.")
                else:
                    self.doc_path = file_path
                    self.doc_entry.delete(0, "end")
                    self.doc_entry.insert(0, file_path)

    def update_screenshot_dir(self):
        """Update the screenshot directory from manual input."""
        if self.use_default_dir.get():
            self.screenshot_dir = self.default_screenshot_dir
        else:
            self.screenshot_dir = self.screenshot_entry.get()
    def update_class(self):
        """Update the class from manual input."""
        if self.use_default_class.get():
            self.current_class = self.default_class
        else:
            self.current_class = self.class_entry.get()

    #add file already exists check if the we are adding a new file
    def update_doc_path(self):
        """Validate the document path based on the selected mode."""
        file_path = self.doc_entry.get().strip()

        if self.mode_var.get() == "new":
            # Get the entered filename
            file_name = self.fileName_entry.get().strip()

            if file_name:
                self.doc_path = os.path.join(file_path, f"{file_name}.pdf")
            else:
                self.doc_path = os.path.join(file_path, "new_autodoc_file.pdf")
        else:
            self.doc_path = file_path

    def start_monitoring(self):
        """Start monitoring clipboard for screenshots."""
        
        if not self.screenshot_dir or not self.doc_path:
            messagebox.showwarning("Warning", "Please select valid directories first!")
            return

        if not os.path.isdir(self.screenshot_dir):
            messagebox.showwarning("Warning", "Please select a valid screenshot directory")
            return

        # If in 'new' mode, check if the directory exists instead of checking for a file
        if self.mode_var.get() == "new":
            doc_dir = os.path.dirname(self.doc_path)
            if not os.path.isdir(doc_dir):
                messagebox.showwarning("Warning", "Please select a valid directory for the PDF file.")
                return
        else:
            # For 'existing' mode, check if the file exists and is a valid PDF
            if not (os.path.isfile(self.doc_path) and self.doc_path.lower().endswith(".pdf")):
                messagebox.showwarning("Warning", "Please select an existing PDF file.")
                return

        self.ok_button.place_forget()
        self.doc = PdfSaver(self.prompt_mode_var.get(), self.doc_path, self.title_entry.get().strip(), self.exercise_entry.get().strip(),
                            self.name_entry.get().strip(), self.surname_entry.get().strip(), self.class_entry.get().strip())

        # Hide initial setup UI
        for widget in self.root.winfo_children():
            widget.pack_forget()
        
        self.screenshot_label = CTkLabel(self.root, text="No new screenshots taken")
        self.screenshot_label.pack(pady=50)
        self.image_label.pack()

        # Start checking clipboard
        self.check_clipboard()


    def check_clipboard(self):
        """Continuously monitor the clipboard for new screenshots."""
        try:
            image = ImageGrab.grabclipboard()
            if isinstance(image, ImageGrab.Image.Image) and image != self.previous_image:
                self.display_screenshot(image)
                self.previous_image = image
            else:
                self.root.after(1000, self.check_clipboard)
        except KeyboardInterrupt:
            print("\nStopping clipboard monitoring. Goodbye!")

    def display_screenshot(self, image):
        """Display the screenshot in the UI for user approval."""
        if self.auto_popUp.get():
            self.raise_above_all()
        self.current_screenshot = image.copy()  # Keep the full-quality image for saving

        # Get the image size
        width, height = image.size
        
        # Define a maximum width and height for the display
        max_width, max_height = 400, 300

        # Calculate the aspect ratio
        aspect_ratio = width / height

        # Resize the image while maintaining the aspect ratio
        if width > max_width or height > max_height:
            if aspect_ratio > 1:  # Landscape image
                new_width = max_width
                new_height = int(new_width / aspect_ratio)
            else:  # Portrait or square image
                new_height = max_height
                new_width = int(new_height * aspect_ratio)
            resized_image = image.resize((new_width, new_height))
        else:
            resized_image = image

        # Convert to CTkImage before setting it
        ctk_image = CTkImage(light_image=resized_image, size=(resized_image.width, resized_image.height))
        self.image_label.configure(image=ctk_image)
        self.image_label.image = ctk_image  # Keep a reference!
        self.image_label.pack(pady=5)
        self.prompt_entry.pack(pady=5)
        self.save_button.pack(pady=8)
        self.discard_button.pack(pady=8)

    def save_screenshot(self):
        """Saves the screenshot and user-provided description to the document."""
        if self.current_screenshot is None:
            return

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = os.path.join(self.screenshot_dir, f"screenshot_{timestamp}.png")
        description = self.prompt_entry.get("1.0", "end-1c").strip() or "Here enter the screenshot description"

        try:
            # Save the screenshot as a PNG
            self.current_screenshot.save(filename, "PNG")
            self.doc.addImage(filename, description)
            print(f"Screenshot saved: {filename}")
            messagebox.showinfo("Success", "Screenshot saved to document!")

            self.reset_screen()
        except Exception as e:
            messagebox.showerror("Error", f"Could not save screenshot: {e}")

        if self.auto_minimalize.get():
            self.minimalize()

    def discard_screenshot(self):
        """Discards the current screenshot."""
        self.current_screenshot = None
        messagebox.showinfo("Discarded", "Screenshot discarded.")
        self.reset_screen()

        if self.auto_minimalize.get():
            self.minimalize()

    def reset_screen(self):
        """Resets the UI back to 'no new screenshots' state."""
        self.screenshot_label.configure(text="No new screenshots taken")
        self.prompt_entry.pack_forget()
        self.save_button.pack_forget()
        self.discard_button.pack_forget()
        self.image_label.configure(image="")  # Clear image preview
        self.image_label.pack_forget()  # Hide image label
        self.current_screenshot = None

        # Clear the clipboard to prevent the same screenshot from being detected again
        self.root.clipboard_clear()
        
        # Delay clipboard checking to ensure the UI resets properly
        self.root.after(1500, self.check_clipboard)


class PdfSaver:
    def __init__(self, prompt_mode="regular", filename="", title="", exercise_number="", name="", surname="", student_class=""):
        self.filename = filename
        self.title = title
        self.count = 1
        self.prompt_mode = prompt_mode  # "regular" (default) or "numbered"
        self.width, self.height = letter
        self.description_height = 20
        self.segment_height = self.height / 2
        self.image_margin = 10
        self.image_width = self.width - self.image_margin * 2
        self.image_height = self.segment_height - self.description_height - self.image_margin * 2
        self.temporary_addition_path = os.path.join(os.path.dirname(__file__), "temp_add.pdf")

        self.register_fonts()

        if not os.path.exists(self.filename):
            self.create_pdf(exercise_number, title, name, surname, student_class)
            self.save_count()
        else:
            self.count, self.prompt_mode = self.load_count()  # Load both count and mode

    def register_fonts(self):
        try:
            pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
            print("Font registration successful")
        except Exception as e:
            print(f"Font registration failed: {e}")

    def create_pdf(self, exercise_number, title, name, surname, student_class):
        self.pdf = canvas.Canvas(self.filename)
        self.pdf.setTitle(title)

        self.pdf.setFont('DejaVuSans', 14)
        self.pdf.drawCentredString(self.width / 2, self.height - 120, f"CV {exercise_number}")
        self.pdf.drawCentredString(self.width / 2, self.height - 140, title)

        self.pdf.setFont('DejaVuSans', 12)
        self.pdf.drawCentredString(self.width / 2, self.height - 180, f"{name} {surname}")
        self.pdf.drawCentredString(self.width / 2, self.height - 200, f"Třída: {student_class}")

        current_date = datetime.now().strftime("%d. %m. %Y")
        self.pdf.drawCentredString(self.width / 2, 40, f"Datum: {current_date}")

        self.pdf.save()
        print("Creating PDF")

    def appendPage(self):
        writer = PdfWriter()
        with open(self.filename, "rb") as existing_file:
            reader = PdfReader(existing_file)
            for page in range(len(reader.pages)):
                writer.add_page(reader.pages[page])

            with open(self.temporary_addition_path, "rb") as new_file:
                new_reader = PdfReader(new_file)
                writer.add_page(new_reader.pages[0])

        with open(self.filename, "wb") as output_file:
            writer.write(output_file)
        print("Appending page")

    def addImage(self, path, description):
        self.pdf = canvas.Canvas(self.temporary_addition_path) 
        self.pdf.setTitle(self.title) 

        img = Image.open(path)
        img_width, img_height = img.size

        aspect_ratio = img_width / img_height
        if self.image_width / self.image_height > aspect_ratio:
            new_height = self.image_height
            new_width = self.image_height * aspect_ratio
        else:
            new_width = self.image_width
            new_height = self.image_width / aspect_ratio
        
        font_size = 15
        max_width = self.width - 40
        self.pdf.setFont('DejaVuSans', font_size)

        # Decide numbering based on prompt_mode
        description_text = f"{self.count}. {description}" if self.prompt_mode == "numbered" else description
        lines = self.wrap_text(description_text, font_size, max_width)

        y_position = self.height - 50  
        for line in lines:
            self.pdf.drawCentredString(self.width / 2, y_position, line)
            y_position -= font_size + 4
            
        self.pdf.drawImage(path, self.width / 2 - new_width / 2, self.height / 2 - new_height / 2, new_width, new_height) 
        self.pdf.showPage()
        self.pdf.save()

        self.appendPage()
        self.count += 1
        self.save_count()
        print("Adding image")

    def wrap_text(self, description, font_size, max_width):
        lines = []
        self.pdf.setFont('DejaVuSans', font_size)

        paragraphs = description.split("\n")
        for paragraph in paragraphs:
            words = paragraph.split()
            current_line = ""

            for word in words:
                test_line = current_line + " " + word if current_line else word
                line_width = self.pdf.stringWidth(test_line)

                if line_width < max_width:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word
            
            if current_line:
                lines.append(current_line)
        
        return lines

    def get_file_key(self, filename):
        return hashlib.md5(os.path.abspath(filename).encode()).hexdigest()

    def save_count(self):
        count_file = "count.json"
        file_key = self.get_file_key(self.filename)

        if os.path.exists(count_file):
            with open(count_file, "r") as file:
                try:
                    count_data = json.load(file)
                except json.JSONDecodeError:
                    count_data = {}
        else:
            count_data = {}

        count_data[file_key] = {
            "count": self.count,
            "prompt_mode": self.prompt_mode  # Save prompt_mode as well
        }

        with open(count_file, "w") as file:
            json.dump(count_data, file, indent=4)

    def load_count(self):
        count_file = "count.json"
        file_key = self.get_file_key(self.filename)
        if os.path.exists(count_file):
            with open(count_file, "r") as file:
                try:
                    count_data = json.load(file)
                except json.JSONDecodeError:
                    return 1, "regular"

                file_data = count_data.get(file_key, {"count": 1, "prompt_mode": "regular"})
                return file_data.get("count", 1), file_data.get("prompt_mode", "regular")
        return 1, "regular"
    
if __name__ == "__main__":
    root = CTk()
    set_default_color_theme("blue")
    set_appearance_mode("Dark") 
    app = ScreenshotApp(root)
    root.mainloop()
