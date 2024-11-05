from io import BytesIO

import qrcode
from barcode import Code128
from barcode.writer import ImageWriter
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from config import AppConfig


class PDF_generator:
    def __init__(self):
        pass

    def generate_barcode(self, input_string):
        try:
            barcode_io = BytesIO()
            # file_name = "barcode"
            my_code = Code128(input_string, writer=ImageWriter())
            my_code.write(barcode_io)
            barcode_io.seek(0)
            # my_code.save(file_name)  # Save the barcode as "barcode.png"
            # return f"{file_name}.png"  # Return the file path for later use
            return barcode_io
        except Exception as e:
            self.error_generator.display_error("Error", str(e))
            return None

    def generate_qr_code(self, input_string):
        try:
            qr_io = BytesIO()
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(input_string)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")
            img.save(qr_io, format="PNG")
            qr_io.seek(0)
            return qr_io  # Return the file path for later use
        except Exception as e:
            self.error_generator.display_error("Error", str(e))
            return None

    def generate_pdf(self, details):
        item_name = details.get("name")
        volume = details.get("volume")
        concentration = details.get("concentration")
        barcode_input = details.get("barcode input")
        qr_code_input = details.get("qr code input")
        page_size = details.get("page size")
        page_size = landscape(A4) if page_size == "Landscape" else A4

        fileName = "output.pdf"
        documentTitle = f"{item_name} Inventory Label"

        # image paths found in the AppConfig class
        logo_path = AppConfig.SOFAB_LOGO
        flame_path = AppConfig.FLAME

        # Creating a pdf object
        pdf = canvas.Canvas(fileName)

        pdf.setPageSize(page_size)
        pdf.setTitle(documentTitle)

        pdf.rect(10, 25, 565, 245, stroke=1, fill=0)

        # Adding multiline text from the Text widget
        pdf.setFont("Helvetica", 16)
        pdf.setFillColor(colors.black)
        text_obj = pdf.beginText(20, 250)

        # for line in text.splitlines():
        #     text_obj.textLine(line)
        # pdf.drawText(text_obj)

        # Draw chemical info

        pdf.setFont("Helvetica-Bold", 25)
        pdf.drawString(20, 350, "Chemical Name:")
        pdf.setFont("Helvetica", 25)
        pdf.drawString(250, 350, item_name)

        pdf.setFont("Helvetica-Bold", 25)
        pdf.drawString(20, 300, "Volume:")
        pdf.setFont("Helvetica", 25)
        pdf.drawString(250, 300, volume)

        pdf.setFont("Helvetica-Bold", 25)
        pdf.drawString(20, 450, "Concentration:")
        pdf.setFont("Helvetica", 25)
        pdf.drawString(250, 450, concentration)

        barcode_io = self.generate_barcode(barcode_input)

        # Draw barcode and QR code images
        if barcode_io:
            barcode_image = ImageReader(barcode_io)
            pdf.drawImage(barcode_image, 460, 435, width=200, height=150)
        # if qr_code_path:
        #     pdf.drawInlineImage(qr_code_path, 645, 415, width=200, height=200)

        # Draw additional images (logo and flame)
        pdf.drawInlineImage(
            str(logo_path),
            0,
            475,
            width=None,
            height=None,
            preserveAspectRatio=True,
        )
        pdf.drawInlineImage(
            str(flame_path),
            580,
            30,
            width=250,
            height=300,
            preserveAspectRatio=True,
        )

        # Add precautions text
        #  pdf.setFont("Helvetica-Bold", 25)
        # pdf.drawString(20, 450, 'Precautions:')
        # pdf.setFont("Helvetica", 16)
        # precaution_text_obj = pdf.beginText(20, 420)
        # for line in precautions.splitlines():
        #     precaution_text_obj.textLine(line)
        # pdf.drawText(precaution_text_obj)

        # Saving the pdf
        pdf.save()
