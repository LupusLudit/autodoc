import os
from datetime import datetime
from PIL import ImageGrab
from customtkinter import*
from tkinter import filedialog, messagebox
from datetime import datetime
from pdfsaver import PdfSaver
from settings import SettingsMenu

class ScreenshotApp():
    def __init__(self, root):
        # Window settings / main variables
        self.root = root
        self.assets_path = os.path.join(os.getcwd(), "assets")
        self.include_path = os.path.join(os.getcwd(), "include")
        self.root.iconbitmap(os.path.join(self.assets_path, "icon.ico"))
        self.root.title("Auto Screenshot Documenter")
        self.root.geometry("1024x950")

        #==Cavas and a scrollable frame==

        self.canvas = CTkCanvas(root, borderwidth=0, highlightthickness=0)
        self.scrollbar = CTkScrollbar(root, orientation="vertical", command=self.canvas.yview)
        self.scrollable_frame = CTkFrame(self.canvas, corner_radius=0)
        self.settings_menu = SettingsMenu(self.scrollable_frame, self.assets_path)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        # Placing the frame inside the canvas at coordinate (0,0).
        self.scrollable_frame_id = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        # Connecting Canvas and Scrollbar
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        # Adjusting the Frame Size on Canvas Resize
        self.canvas.bind("<Configure>", self.adjust_scrollable_frame)

        # Variables for paths
        self.screenshot_dir = None
        self.doc_path = None
        self.current_class = None
        self.current_screenshot = None
        self.screenshot_preview = None
        self.previous_image = None
        self.doc = None

        self.mode_var = StringVar(value="new")
        self.use_default_dir = BooleanVar(value=False)
        self.use_default_class = BooleanVar(value=False)

        self.default_screenshot_dir = os.path.join(os.getcwd(), "img")
        self.default_class = "C3a"

        #==UI Elements==

        CTkLabel(self.scrollable_frame, text="Choose Mode:").pack(pady=5)
        CTkRadioButton(self.scrollable_frame, text="Create New PDF", variable=self.mode_var, value="new", command=self.toggle_mode).pack()
        CTkRadioButton(self.scrollable_frame, text="Open Existing PDF", variable=self.mode_var, value="existing", command=self.toggle_mode).pack()

        CTkCheckBox(self.scrollable_frame, text="Use default screenshot directory",
                     variable=self.use_default_dir, onvalue=True, offvalue=False,
                     command=self.toggle_default_dir).pack()

        CTkLabel(self.scrollable_frame, text="Select Screenshot Directory:").pack(pady=5)
        self.screenshot_entry = CTkEntry(self.scrollable_frame, width=500)
        self.screenshot_entry.pack(pady=5)
        self.screenshot_entry.bind("<KeyRelease>", lambda e: self.update_screenshot_dir())
        self.screenshot_browse_button = CTkButton(self.scrollable_frame, text="Browse", command=self.set_screenshot_dir, corner_radius=15)
        self.screenshot_browse_button.pack()

        CTkLabel(self.scrollable_frame, text="Select Document File:").pack(pady=5)
        self.doc_entry = CTkEntry(self.scrollable_frame, width=500)
        self.doc_entry.pack(pady=5)
        self.doc_entry.bind("<KeyRelease>", lambda e: self.update_doc_path())
        CTkButton(self.scrollable_frame, text="Browse", command=self.browse_doc, corner_radius=15).pack(pady=10)

        self.metadata_frame = CTkFrame(self.scrollable_frame)
        self.metadata_frame.pack(pady=10)

        CTkLabel(self.metadata_frame, text="Enter new file name:").pack(pady=5)
        self.fileName_entry = CTkEntry(self.metadata_frame, width=300)
        self.fileName_entry.pack(pady=5)
        self.fileName_entry.bind("<KeyRelease>", lambda e: self.update_doc_path())
        self.fileName_entry.configure(placeholder_text="CVnumber_Surname_ExerciseTitle")

        vcmd = root.register(self.validate_numeric_input)

        CTkLabel(self.metadata_frame, text="Enter Exercise number:").pack(pady=5)
        self.exercise_entry = CTkEntry(self.metadata_frame, width=150, validate="key", validatecommand=(vcmd, '%P'))
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

        CTkCheckBox(self.metadata_frame, text="Use default class name",
                    variable=self.use_default_class, onvalue=True, offvalue=False,
                    command=self.toggle_default_class).pack()

        CTkLabel(self.metadata_frame, text="Enter your class name (school class):").pack(pady=5)
        self.class_entry = CTkEntry(self.metadata_frame, width=300)
        self.class_entry.pack(pady=5)
        self.class_entry.bind("<KeyRelease>", lambda e: self.update_class())
        self.class_entry.configure(placeholder_text="C3a")
        
        self.prompt_mode_var = StringVar(value="regular")

        CTkLabel(self.metadata_frame, text="Choose prompt mode:").pack(pady=5)
        CTkRadioButton(self.metadata_frame, text="Regular prompts (no numbering)", variable=self.prompt_mode_var, value="regular").pack()
        CTkRadioButton(self.metadata_frame, text="Automatic prompt numbering", variable=self.prompt_mode_var, value="numbered").pack()

        # OK Button
        self.ok_button = CTkButton(self.scrollable_frame, text="OK", command=self.start_monitoring,
                                fg_color="lime green", text_color="black", 
                                corner_radius=20, border_width=2, border_color="green",
                                hover_color="#90ee90")
        self.ok_button.pack(pady=20)

        # Close Button
        self.close_button = CTkButton(self.scrollable_frame, text="CLOSE", command=root.quit,
                fg_color="red", text_color="white",
                corner_radius=20, border_width=2, border_color="dark red",
                hover_color="#ff6666")
        self.close_button.pack(pady=20)

        #==Initially hidden elements==

        self.image_label = CTkLabel(root, text="")
        self.image_label.pack_forget()

        self.prompt_entry = CTkTextbox(root, width=600, height=200, wrap="word")
        self.prompt_entry.insert("1.0", "Here enter the screenshot description")
        self.prompt_entry.pack_forget()

        self.save_button = CTkButton(root, text="SAVE", command=self.save_screenshot,
                            fg_color="lime green", text_color="black", 
                            corner_radius=20, border_width=2, border_color="green",
                            hover_color="#90ee90")
        self.save_button.pack_forget()

        self.discard_button = CTkButton(root, text="DISCARD", command=self.discard_screenshot,
                                fg_color="red", text_color="white",
                                corner_radius=20, border_width=2, border_color="dark red",
                                hover_color="#ff6666")
        self.discard_button.pack_forget()

        self.save_hint_label = CTkLabel(root, text="Press 'Ctrl + S' to save the screenshot")
        self.save_hint_label.pack_forget()

        self.discard_hint_label = CTkLabel(root, text="Press 'Ctrl + Del' to discard the screenshot")
        self.discard_hint_label.pack_forget()

        root.bind("<Control-s>", self.save_screenshot)
        root.bind("<Control-Delete>", self.discard_screenshot)
        self.toggle_mode()

    def _on_mousewheel(self, event):
        """Scrolls the canvas when the mouse wheel is used."""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def adjust_scrollable_frame(self, event):
        """Adjusts the size of the scrollable frame to match the canvas size."""
        # Make sure the frame inside always matches the canvas width
        canvas_width = event.width
        canvas_height = event.height
        self.canvas.itemconfig(self.scrollable_frame_id, width=canvas_width)

        # Ensure the scrollable_frame has at least the same height as the canvas
        self.scrollable_frame.update_idletasks() 
        frame_height = self.scrollable_frame.winfo_height()

        # If the frame is shorter than the window, stretch it to at least match the canvas height
        if frame_height < canvas_height:
            self.canvas.itemconfig(self.scrollable_frame_id, height=canvas_height)
        else:
            self.canvas.itemconfig(self.scrollable_frame_id, height=frame_height)

        self.update_scrollregion()


    def update_scrollregion(self):
        """Sets the scroll area to the bounding box that contains all items in the canvas."""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    ## ====================
    ## ==USER PREFERENCES==
    ## ====================
    
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
            self.ok_button.pack_forget()
            self.close_button.pack_forget()
            self.metadata_frame.pack(pady=10)
            self.ok_button.pack(pady=20)
            self.close_button.pack(pady=10)
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

    ## ===================
    ## =====MAIN CODE=====
    ## ===================

    def validate_numeric_input(self, value):
        """Make sure the the input is numeric or empty."""
        return value.isdigit() or value == ""

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
        if self.settings_menu.auto_popUp.get():
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
        self.save_hint_label.pack(pady=5)
        self.discard_hint_label.pack(pady=5)

    def save_screenshot(self, event=None):
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

        if self.settings_menu.auto_minimalize.get():
            self.minimalize()

    def discard_screenshot(self, event=None):
        """Discards the current screenshot."""
        self.current_screenshot = None
        messagebox.showinfo("Discarded", "Screenshot discarded.")
        self.reset_screen()

        if self.settings_menu.auto_minimalize.get():
            self.minimalize()

    def reset_screen(self):
        """Resets the UI back to 'no new screenshots' state."""
        self.screenshot_label.configure(text="No new screenshots taken")
        self.prompt_entry.pack_forget()
        self.save_button.pack_forget()
        self.discard_button.pack_forget()
        self.save_hint_label.pack_forget()
        self.discard_hint_label.pack_forget()
        self.image_label.configure(image="")  # Clear image preview
        self.image_label.pack_forget()  # Hide image label
        self.current_screenshot = None

        # Clear the clipboard to prevent the same screenshot from being detected again
        self.root.clipboard_clear()
        
        # Delay clipboard checking to ensure the UI resets properly
        self.root.after(1500, self.check_clipboard)