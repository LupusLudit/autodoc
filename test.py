from reportlab.pdfgen import canvas 
from reportlab.pdfbase.ttfonts import TTFont 
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.pagesizes import letter
from PIL import Image
from PyPDF2 import PdfReader, PdfWriter
import os
from datetime import datetime

class DocumentSaver:
    def __init__(self, filename, title, exercise_number, name, surname, student_class):
        self.filename = os.path.join(os.path.dirname(__file__), filename)
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

doc = DocumentSaver("file.pdf", "title", "1", "FP", "HP", "C3a")

image_path = os.path.join(os.path.dirname(__file__), "img", "folder.png")
doc.addImage(image_path, "a")
doc.addImage(image_path, "b")
doc.addImage(image_path, "c")
doc.addImage(image_path, "d")
doc.addImage(image_path, "e")
doc.addImage(image_path, "f")

