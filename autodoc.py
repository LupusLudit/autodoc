import os
from datetime import datetime
from PIL import ImageGrab, ImageTk
from tkinter import Tk, Label, Entry, Button, filedialog, messagebox, StringVar, Radiobutton, Frame, Text
import json
import hashlib
from reportlab.pdfgen import canvas 
from reportlab.pdfbase.ttfonts import TTFont 
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.pagesizes import letter
from PIL import Image
from PyPDF2 import PdfReader, PdfWriter
from datetime import datetime

#pip install PyPDF2
#pip install reportlab

#Note: The pdf file cannot be opened in another program while using autodoc

class ScreenshotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Auto Screenshot Documenter")
        self.root.geometry("1024x800")

        # Variables for paths
        self.screenshot_dir = None
        self.doc_path = None
        self.current_screenshot = None
        self.screenshot_preview = None
        self.previous_image = None
        self.doc = None

        # Mode Selection (Existing file or New file)
        self.mode_var = StringVar(value="new")  # Default: create new file

        Label(root, text="Choose Mode:").pack(pady=5)
        Radiobutton(root, text="Create New PDF", variable=self.mode_var, value="new", command=self.toggle_mode).pack()
        Radiobutton(root, text="Open Existing PDF", variable=self.mode_var, value="existing", command=self.toggle_mode).pack()

        # UI Elements for path selection
        Label(root, text="Select Screenshot Directory:").pack(pady=5)
        self.screenshot_entry = Entry(root, width=75)
        self.screenshot_entry.pack(pady=5)
        self.screenshot_entry.bind("<KeyRelease>", lambda e: self.update_screenshot_dir())
        Button(root, text="Browse", command=self.set_screenshot_dir).pack()

        Label(root, text="Select Document File:").pack(pady=5)
        self.doc_entry = Entry(root, width=75)
        self.doc_entry.pack(pady=5)
        self.doc_entry.bind("<KeyRelease>", lambda e: self.update_doc_path())
        Button(root, text="Browse", command=self.browse_doc).pack()

        # Metadata fields (Only shown for new PDFs)
        self.metadata_frame = Frame(root)
        self.metadata_frame.pack(pady=10)

        Label(self.metadata_frame, text="Enter new file name:").pack(pady=5)
        self.fileName_entry = Entry(self.metadata_frame, width=50)
        self.fileName_entry.pack(pady=5)
        self.fileName_entry.bind("<KeyRelease>", lambda e: self.update_doc_path())

        Label(self.metadata_frame, text="Enter Exercise number:").pack(pady=5)
        self.exercise_entry = Entry(self.metadata_frame, width=50)
        self.exercise_entry.pack(pady=5)

        Label(self.metadata_frame, text="Enter Main Title:").pack(pady=5)
        self.title_entry = Entry(self.metadata_frame, width=50)
        self.title_entry.pack(pady=5)

        Label(self.metadata_frame, text="Enter your name:").pack(pady=5)
        self.name_entry = Entry(self.metadata_frame, width=50)
        self.name_entry.pack(pady=5)

        Label(self.metadata_frame, text="Enter your surname:").pack(pady=5)
        self.surname_entry = Entry(self.metadata_frame, width=50)
        self.surname_entry.pack(pady=5)

        Label(self.metadata_frame, text="Enter your Class:").pack(pady=5)
        self.class_entry = Entry(self.metadata_frame, width=50)
        self.class_entry.pack(pady=5)
        
        self.prompt_mode_var = StringVar(value="regular")

        Label(self.metadata_frame, text="Choose prompt mode:").pack(pady=5)
        Radiobutton(self.metadata_frame, text="Regular prompts (no numbering)", variable=self.prompt_mode_var, value="regular").pack()
        Radiobutton(self.metadata_frame, text="Automatic prompt numbering", variable=self.prompt_mode_var, value="numbered").pack()

        # OK Button
        self.ok_button = Button(root, text="OK", command=self.start_monitoring, fg="black", bg="lime", font=("Arial", 12), relief="raised")
        self.ok_button.place(relx=0.5, rely=1.0, anchor="s", y=-10)  # Centered at the bottom

        # Close Button
        Button(root, text="CLOSE", command=root.quit).place(relx=1.0, rely=1.0, x=-10, y=-10, anchor="se")

        self.image_label = Label(root)  
        self.image_label.pack(pady=10)

        # Screenshot Description (Initially Hidden)
        self.prompt_entry = Text(root, width=50, height=7, wrap="word")
        self.prompt_entry.pack(pady=5)
        self.prompt_entry.insert("1.0", "Here enter the screenshot description")
        self.prompt_entry.pack_forget()

        # Save and Discard Buttons (Initially Hidden)
        self.save_button = Button(root, text="SAVE", command=self.save_screenshot, fg="black", bg="lime", font=("Arial", 12, "bold"), relief="raised")
        self.save_button.pack_forget()

        self.discard_button = Button(root, text="DISCARD", command=self.discard_screenshot, fg="black", bg="red", font=("Arial", 12, "bold"), relief="raised")
        self.discard_button.pack_forget()

        self.toggle_mode()  # Initialize correct visibility

    def toggle_mode(self):
        """Show or hide metadata fields based on selected mode."""
        if self.mode_var.get() == "new":
            self.metadata_frame.pack(pady=10)
            self.doc_entry.delete(0, "end")
            self.doc_entry.insert(0, "Choose directory for new PDF")
        else:
            self.metadata_frame.pack_forget()
            self.doc_entry.delete(0, "end")
            self.doc_entry.insert(0, "Choose existing PDF file")

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
        self.screenshot_dir = self.screenshot_entry.get()


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
        self.doc = PdfSaver(self.prompt_mode_var.get(), self.doc_path, self.exercise_entry.get().strip(), self.title_entry.get().strip(),
                            self.name_entry.get().strip(), self.surname_entry.get().strip(), self.class_entry.get().strip())

        # Hide initial setup UI
        for widget in self.root.winfo_children():
            widget.pack_forget()
        
        self.screenshot_label = Label(self.root, text="No new screenshots taken", fg="gray")
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

        # Convert the image to a Tkinter-compatible photo image
        self.screenshot_preview = ImageTk.PhotoImage(resized_image)

        # Update UI
        self.image_label.config(image=self.screenshot_preview)
        self.image_label.pack(pady=5)
        self.screenshot_label.config(text="New screenshot detected!")
        self.prompt_entry.pack(pady=5)
        self.save_button.pack(pady=5)
        self.discard_button.pack(pady=5)

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

    def discard_screenshot(self):
        """Discards the current screenshot."""
        self.current_screenshot = None
        messagebox.showinfo("Discarded", "Screenshot discarded.")
        self.reset_screen()

    def reset_screen(self):
        """Resets the UI back to 'no new screenshots' state."""
        self.screenshot_label.config(text="No new screenshots taken")
        self.prompt_entry.pack_forget()
        self.save_button.pack_forget()
        self.discard_button.pack_forget()
        self.image_label.config(image="")  # Clear image preview
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
        self.pdf.drawCentredString(self.width / 2, self.height - 180, f"Jméno a příjmení: {name} {surname}")
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
    root = Tk()
    app = ScreenshotApp(root)
    root.mainloop()
