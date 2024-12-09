import customtkinter
import tkinter as tk
from tkinter import ttk

from PIL import Image, ImageTk, ImageGrab
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from PIL import Image as PILImage
import os

from config import AppConfig

class PDFGenerator:
    def __init__(self,frame,widgets):
        self.save_pdf_callback = None

        self.frame = frame
        self.widgets = widgets

    def export_to_pdf(self,frame=customtkinter.CTkFrame,window=customtkinter.CTkFrame):
       # Create a PDF canvas
       c = canvas.Canvas("preview_frame_output.pdf",pagesize=A4)

       # Get the frame's coordinates and size
       x, y = frame.winfo_rootx(), frame.winfo_rooty()
       width, height = frame.winfo_width(), frame.winfo_height()
       print(width, height)
       # Draw the frame's contents on the canvas
       c.drawString(0.5 * inch, 8.5 * inch, "Frame Content")

       # Save the PDF
       c.save()

    def extract_widgets_and_draw(self, c, frame, widgets, x, y, frame_width, frame_height):
        for widget in widgets:
            widget_type = type(widget)
            
            if isinstance(widget, customtkinter.CTkLabel):  # Handle CTkLabel (both text and image)
                # Check if the label contains an image or text
                image = widget.cget("image")
                if image:  # If the label has an image
                    try:
                        pil_image = image.cget("dark_image")  # Open the image using Pillow
                        image_path = "tmpimage.png"  # Get the image name (for saving locally)
                        pil_image.save(image_path)  # Save the image temporarily
                        c.drawImage(image_path, x + 10, y + frame_height - 80, width=100, height=100)
                        os.remove(image_path)  # Remove the temporary image file after use
                    except Exception as e:
                        print(f"Error loading image: {e}")
                else:  # If the label contains text
                    text = widget.cget("text")
                    c.setFont("Helvetica", 12)
                    c.drawString(x + 10, y + frame_height - 30, text)

    def save_to_pdf(self):
        c = canvas.Canvas("preview_frame_output.pdf",pagesize=A4)
        width, height = landscape(A4)
        frame_width = width / 4  # 4 frames horizontally
        frame_height = height / 2  # 2 frames vertically

        for row in range(2):  # 2 rows
            for col in range(4):  # 4 columns
                # Calculate the position of each frame
                x_position = col * frame_width
                y_position = height - (row + 1) * frame_height  # Y starts from bottom
                
                # Extract widgets from the frame and draw them on the canvas
                self.extract_widgets_and_draw(c, self.frame, self.widgets, x_position, y_position, frame_width, frame_height)
                break
        
        c.save()
    
    
    def save_to_pdf2(self):
        tmp_png = "preview_frame_output.png"
        self.capture_widget_as_image(self.frame, tmp_png)
        self.create_pdf(tmp_png, "preview_frame_output.pdf")
        os.remove(tmp_png)

    def capture_widget_as_image(self,widget, filename="widget_capture.png"):
        # Get the widget's bounding box
        x = widget.winfo_rootx()
        y = widget.winfo_rooty()
        width = widget.winfo_width()
        height = widget.winfo_height()

        img = ImageGrab.grab(bbox=(x, y, (x + width), (y + height)))
        new_image = img.rotate(-90)
        new_image = img.convert("RGB")
        

        new_image.save(filename)

    def create_pdf(self,image_path, pdf_filename="output.pdf"):
        page_width, page_height = landscape(A4)  # A4 landscape size (842.0 x 595.276)

        c = canvas.Canvas(pdf_filename, pagesize=(page_width, page_height))
        img = Image.open(image_path)
        
        img_width, img_height = img.size

        scale_factor = min(page_width / img_width, page_height / img_height)

        new_width = img_width * scale_factor
        new_height = img_height * scale_factor
        x_offset = (page_width - new_width) / 2
        y_offset = (page_height - new_height) / 2
        c.drawImage(image_path, x_offset, y_offset+20, width=new_width * 0.25, height=new_height * 0.25)
        c.drawImage(image_path, x_offset+200, y_offset+200, width=new_width * 0.5, height=new_height * 0.5)
        c.save()
    
    def export_to_pdf_custom(self,frame,frame_children):
        c = canvas.Canvas("preview_frame_output.pdf",pagesize=A4)

        for widget in frame_children:
            widget_type = type(widget)
            #print(widget_type)

            if isinstance(widget, customtkinter.CTkLabel):
                image = widget.cget("image")
                if image:  # If the label has an image
                    try:
                        pil_image = PILImage.open(image)  # Open the image using Pillow
                        image_path = image.split("/")[-1]  # Get the image name (for saving locally)
                        pil_image.save(image_path)  # Save the image temporarily
                        c.drawImage(image_path, x + 10, y + frame_height - 80, width=100, height=100)
                        os.remove(image_path)  # Remove the temporary image file after use
                    except Exception as e:
                        print(f"Error loading image: {e}")