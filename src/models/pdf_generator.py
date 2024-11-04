import qrcode
from barcode import Code128
from barcode.writer import ImageWriter
from reportlab.lib import colors
from reportlab.pdfgen import canvas


class PDF_generator:
    def __init__(self):
        pass

    def generate_barcode(self, input_string):
        try:
            file_name = "barcode"
            my_code = Code128(input_string, writer=ImageWriter())
            my_code.save(file_name)  # Save the barcode as "barcode.png"
            return f"{file_name}.png"  # Return the file path for later use
        except Exception as e:
            self.error_generator.display_error("Error", str(e))
            return None

    def generate_qr_code(self, input_string):
        try:
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(input_string)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")
            file_name = "qr_code"
            img.save(f"{file_name}.png")
            return f"{file_name}.png"  # Return the file path for later use
        except Exception as e:
            self.error_generator.display_error("Error", str(e))
            return None

    def generate_pdf(
        self,
        batch,
        date,
        concentration,
        volume,
        barcode_path,
        qr_code_path,
        page_size,
        text,
    ):
        fileName = "output.pdf"
        documentTitle = "Generated PDF"

        # Paths for additional images

        # Retrieve path for logo
        # relative_path = './sofab_logo.png'
        # logo = os.path.abspath(relative_path)
        logo = "sofab_logo.png"
        # logo = os.path.normpath(absolute_path).replace('\\', '/')  # Update with the correct path
        # logo = absolute_path).replace('\\', '/')  # Update with the correct path
        flame = "flame.png"  # Update with the correct path

        # Creating a pdf object
        pdf = canvas.Canvas(fileName)

        pdf.setPageSize(page_size)
        pdf.setTitle(documentTitle)

        pdf.rect(10, 25, 565, 245, stroke=1, fill=0)

        # Adding multiline text from the Text widget
        pdf.setFont("Helvetica", 16)
        pdf.setFillColor(colors.black)
        text_obj = pdf.beginText(20, 250)
        for line in text.splitlines():
            text_obj.textLine(line)
        pdf.drawText(text_obj)

        # Draw chemical info

        pdf.setFont("Helvetica-Bold", 25)
        pdf.drawString(20, 350, "Chemical Name:")
        pdf.setFont("Helvetica", 25)
        pdf.drawString(250, 350, batch)

        pdf.setFont("Helvetica-Bold", 25)
        pdf.drawString(20, 300, "Volume:")
        pdf.setFont("Helvetica", 25)
        pdf.drawString(250, 300, volume)

        pdf.setFont("Helvetica-Bold", 25)
        pdf.drawString(20, 450, "Concentration:")
        pdf.setFont("Helvetica", 25)
        pdf.drawString(250, 450, concentration)

        pdf.setFont("Helvetica-Bold", 25)
        pdf.drawString(20, 400, "Date Created:")
        pdf.setFont("Helvetica", 25)
        pdf.drawString(250, 400, date)

        # Draw barcode and QR code images
        if barcode_path:
            pdf.drawInlineImage(barcode_path, 460, 435, width=200, height=150)
        if qr_code_path:
            pdf.drawInlineImage(qr_code_path, 645, 415, width=200, height=200)

        # Draw additional images (logo and flame)
        pdf.drawInlineImage(
            logo, 0, 475, width=None, height=None, preserveAspectRatio=True
        )
        pdf.drawInlineImage(
            flame, 580, 30, width=250, height=300, preserveAspectRatio=True
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
