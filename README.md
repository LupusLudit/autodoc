# Autodoc
Autodoc is a Python program that automatically detects screenshots from your clipboard and compiles them into a PDF file. You can add a description for each screenshot, which will later appear alongside the image in the PDF.
The program also offers several user-configurable settings:

* Theme Selection: Choose between dark mode or light mode.
* Automatic Window Pop-Up: Brings the application window to the foreground immediately after taking a screenshot.
* Automatic Window Minimization: Minimizes the window after saving or discarding a screenshot.
* Automatic Alerts: Displays a notification after saving or discarding a screenshot (optional).

## Requirements
* Python installed on your computer.
Recomended python version: 3.13.1 or newer:
[python download](https://www.python.org/downloads/)
The program includes an auto-installer that should automatically install all required packages. If installation fails, manually run the following commands:
```
pip install Pillow
pip install PyPDF2
pip install reportlab
pip install customtkinter
```
These commands will install all necessary dependencies.

## Running the program
Use the run_autodoc.bat file to launch the program. Running the .py files directly may cause errors because the program assumes it is executed from the directory containing run_autodoc.bat, with all file paths set accordingly.

## Important note
This program was originally designed as a helper tool for school exercises. As such, it includes fields like “exercise number” and “school class,” and some PDF fields are in Czech (e.g., Datum = Date).
If you plan to use the program for your own purposes, you may need to adjust these fields. Feel free to modify the code as you see fit.
