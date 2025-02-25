import os
from datetime import datetime
from PIL import ImageGrab, ImageTk
from tkinter import Tk, Label, Entry, Button, filedialog, messagebox, PhotoImage

from reportlab.pdfgen import canvas 
from reportlab.pdfbase.ttfonts import TTFont 
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.pagesizes import letter
from PIL import Image
from PyPDF2 import PdfReader, PdfWriter
import os
from datetime import datetime

#pip install pillow python-docx
#pip install PyPDF2
#pip install reportlab

class ScreenshotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Auto Screenshot Documenter")
        self.root.geometry("1024x720")

        # Variables for paths
        self.screenshot_dir = None
        self.doc_path = None
        self.current_screenshot = None
        self.screenshot_preview = None
        self.previous_image = None
        self.doc = None

        # UI Elements for path selection
        Label(root, text="Select Screenshot Directory:").pack(pady=5)
        self.screenshot_entry = Entry(root, width=50)
        self.screenshot_entry.pack(pady=5)
        Button(root, text="Browse", command=self.set_screenshot_dir).pack()

        Label(root, text="Select Document Directory:").pack(pady=5)
        self.doc_entry = Entry(root, width=50)
        self.doc_entry.pack(pady=5)
        Button(root, text="Browse", command=self.set_doc_dir).pack()

        Label(root, text="Enter Exercise number:").pack(pady=5)
        self.exercise_entry  = Entry(root, width=50)
        self.exercise_entry.pack(pady=5)

        Label(root, text="Enter Main Title:").pack(pady=5)
        self.title_entry  = Entry(root, width=50)
        self.title_entry.pack(pady=5)

        Label(root, text="Enter your name:").pack(pady=5)
        self.name_entry  = Entry(root, width=50)
        self.name_entry.pack(pady=5)

        Label(root, text="Enter your surname:").pack(pady=5)
        self.surname_entry  = Entry(root, width=50)
        self.surname_entry.pack(pady=5)

        Label(root, text="Enter your Class:").pack(pady=5)
        self.class_entry  = Entry(root, width=50)
        self.class_entry.pack(pady=5)

        # Buttons
        Button(root, text="OK", command=self.start_monitoring, 
               fg="black", bg="lime", font=("Arial", 12), relief="raised").pack(pady=10)

        Label()
        # Place the button at bottom-right with margin
        Button(root, text="CLOSE", command=root.quit).place(relx=1.0, rely=1.0, x=-10, y=-10, anchor="se")


        # Placeholder for screenshot preview
        self.image_label = Label(root)  
        self.image_label.pack(pady=10)

        self.prompt_entry = Entry(root, width=50)
        self.prompt_entry.pack(pady=5)
        self.prompt_entry.insert(0, "Here enter the screenshot description")
        self.prompt_entry.pack_forget()  # Hide initially

        self.save_button = Button(root, text="SAVE", command=self.save_screenshot,
                                fg="black", bg="lime", font=("Arial", 12, "bold"), relief="raised")
        self.save_button.pack_forget()

        self.discard_button = Button(root, text="DISCARD", command=self.discard_screenshot,
                                fg="black", bg="red", font=("Arial", 12, "bold"), relief="raised" )
        self.discard_button.pack_forget()

    def set_screenshot_dir(self):
        """Set the directory where screenshots will be saved."""
        directory = filedialog.askdirectory()
        if directory:
            self.screenshot_dir = directory
            self.screenshot_entry.delete(0, "end")
            self.screenshot_entry.insert(0, directory)

    def set_doc_dir(self):
        """Set the PDF file path where the document will be saved."""
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf",
                                                filetypes=[("PDF files", "*.pdf")])
        if file_path:
            self.doc_path = file_path
            self.doc_entry.delete(0, "end")
            self.doc_entry.insert(0, self.doc_path)

    def start_monitoring(self):
        """Start monitoring clipboard for screenshots."""
        if not self.screenshot_dir or not self.doc_path:
            messagebox.showwarning("Warning", "Please select valid directories first!")
            return
        self.doc = PdfSaver(self.doc_path, self.exercise_entry.get().strip(), self.title_entry.get().strip(), self.name_entry.get().strip(), self.surname_entry.get().strip(), self.class_entry.get().strip())
        # Hide initial setup UI
        for widget in self.root.winfo_children():
            widget.pack_forget()
        self.screenshot_label = Label(root, text="No new screenshots taken", fg="gray")
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
        description = self.prompt_entry.get().strip() or "Here enter the screenshot description"

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
    def __init__(self, filename, title, exercise_number, name, surname, student_class):
        self.filename = filename
        self.title = title
        # Get the height of a letter-sized page
        self.width, self.height = letter

        self.description_height = 20

        self.segment_height = self.height / 2

        self.image_margin = 10
        self.image_width = self.width - self.image_margin * 2
        self.image_height = self.segment_height - self.description_height - self.image_margin * 2

        self.temporary_addition_path = os.path.join(os.path.dirname(__file__), "temp_add.pdf")
        

        self.register_fonts()

        if(not os.path.exists(self.filename)):
            self.create_pdf(exercise_number, title, name, surname, student_class)

    def register_fonts(self):
        """Register the DejaVuSans font that supports UTF-8 characters."""
        # Register the DejaVuSans font (you need to have this font file on your system)
        try:
            pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
            print("Font registration succesfull")
        except Exception as e:
            print(f"Font registration failed: {e}")

    def create_pdf(self, exercise_number, title, name, surname, student_class):
        # Initialize canvas
        self.pdf = canvas.Canvas(self.filename)
        self.pdf.setTitle(title)

        # Increase font size for better readability
        self.pdf.setFont('DejaVuSans', 14)

        # Draw exercise title centered at the top of the page
        self.pdf.drawCentredString(self.width / 2, self.height - 120, f"CV {exercise_number}: {title}")
        self.pdf.drawCentredString(self.width / 2, self.height - 140, f"title")

        # Add student information below the title
        self.pdf.setFont('DejaVuSans', 12)
        self.pdf.drawCentredString(self.width / 2, self.height - 180, f"Jméno a příjmení: {name} {surname}")
        self.pdf.drawCentredString(self.width / 2, self.height - 200, f"Třída: {student_class}")

        # Add the current date at the bottom, centered, in Czech format (DD.MM.YYYY)
        current_date = datetime.now().strftime("%d. %m. %Y")  # Format the date in Czech style
        self.pdf.setFont('DejaVuSans', 12)
        self.pdf.drawCentredString(self.width / 2, 40, f"Datum: {current_date}")

        # Save the PDF
        self.pdf.save()
        print("Creating pdf")

    def appendPage(self):
        writer = PdfWriter()

        # Read the existing PDF using PdfReader
        with open(self.filename, "rb") as existing_file:
            reader = PdfReader(existing_file)
            
            # Create a PdfWriter to hold the final output

            # Add all the pages from the existing PDF
            for page in range(len(reader.pages)):
                writer.add_page(reader.pages[page])

            # Add the new page created with ReportLab
            with open(self.temporary_addition_path , "rb") as new_file:
                new_reader = PdfReader(new_file)
                writer.add_page(new_reader.pages[0])

        # Write the combined PDF to the output file
        with open(self.filename, "wb") as output_file:
            writer.write(output_file)
        print("appednding page")

    def addImage(self, path, description):
        self.pdf = canvas.Canvas(self.temporary_addition_path) 
        self.pdf.setTitle(self.title) 

        # Open the image using PIL to get its dimensions
        img = Image.open(path)
        img_width, img_height = img.size

        # Define the region (width and height) where the image should fit
        region_width = self.image_width  # The width of the region
        region_height = self.image_height  # The height of the region

        # Calculate the aspect ratio of the image
        aspect_ratio = img_width / img_height

        # Determine the new width and height to fit the image in the region while maintaining the aspect ratio
        if region_width / region_height > aspect_ratio:
            # Scale based on the height
            new_height = region_height
            new_width = region_height * aspect_ratio
        else:
            # Scale based on the width
            new_width = region_width
            new_height = region_width / aspect_ratio
        
        self.pdf.setFont('DejaVuSans', 18)
        self.pdf.drawCentredString(self.width / 2, self.height - 50, description)
        self.pdf.drawImage(path, self.width / 2 - new_width / 2, self.height / 2 - new_height / 2, new_width, new_height) 
        self.pdf.showPage()

        self.pdf.save()
        self.appendPage()
        print("adding image")

if __name__ == "__main__":
    root = Tk()
    app = ScreenshotApp(root)
    root.mainloop()
