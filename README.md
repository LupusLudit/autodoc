# Autodoc
Written in python. This program automaticly detects screenshots from your clipboard and copies them into a pdf file.
You can add a description for each screenshot, this text would later be displayed in the pdf file with the said screenshot.
The program features some basic user settings:

* Dark mode / light mode theme selection
* Automatic window pop up => makes the window "pop up" if it was minimalized and puts it into foreground right after creating a screenshot
* Automatic window minimalization => minimalizes the window after the user saved/discarded a screenshot
* Automatic alerts => after saving or discarding a screenshot an alert will show up (or not show up depending on users settings) telling the user if the operation was successful.

## Requirements
You need to have python installed on your computer.
Recomended python version: 3.13.1 or newer:
[python download](https://www.python.org/downloads/)
The program also features a autoinstaller that should automaticly install are reqiered packages. In case something goes wrong, run these commands:
```
pip install Pillow
pip install PyPDF2
pip install reportlab
pip install customtkinter
```
That should install all necessary packages.

## Running the program
To run the program, you need to use the run_autodoc.bat file. Running the program directly by using the .py files might result in an error.
The reason behind this is the fact that the program assumes that the directory from which we run the program is the one where the run_autodoc.bat file is contained and all the filepaths used
in the code are set accordingly.

##Important note
Beware that this code was originally intended to be a helper tool to complete school exercises more quickly. For that reason, it includes fields like “exercise number” or “school class.”
It was written in a way to fulfill my professor’s wishes, meaning that some fields in the PDF document are written in Czech (for example, Datum — meaning date).
Therefore, if you intend to use the code for your own purposes, some adjustments will be necessary. You are, of course, free to rewrite the code in whatever way you find suitable.
