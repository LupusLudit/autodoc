import json
import os
import hashlib
from reportlab.pdfgen import canvas 
from reportlab.pdfbase.ttfonts import TTFont 
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.pagesizes import letter
from PIL import Image
from PyPDF2 import PdfReader, PdfWriter
from datetime import datetime
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
        self.include_path = os.path.join(os.getcwd(), "include")
        self.temporary_addition_path = os.path.join(self.include_path, "temp_add.pdf")

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
        count_file = os.path.join(self.include_path, "count.json")
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
        count_file = os.path.join(self.include_path, "count.json")
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