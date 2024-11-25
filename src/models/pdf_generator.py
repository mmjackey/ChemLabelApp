import tempfile

import qrcode
from barcode import Code128
from barcode.writer import ImageWriter
from pylatex import (
    Command,
    Document,
    Head,
    MiniPage,
    PageStyle,
    Section,
    StandAloneGraphic,
    Subsection,
)
from pylatex.package import Package
from pylatex.utils import NoEscape

from config import AppConfig


class PDFGenerator:
    def __init__(self):
        self.save_pdf_callback = None

    def generate_barcode(self, input_string):
        try:
            file_name = "barcode"
            my_code = Code128(input_string, writer=ImageWriter())
            my_code.save(file_name)  # Save the barcode as "barcode.png"
            return f"{file_name}.png"  # Return the file path for later use
        except Exception as e:
            print(e)
            # self.error_generator.display_error("Error", str(e))
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
            print(e)
            # self.error_generator.display_error("Error", str(e))
            return None

    def create_document(self, orientation, paper_size, item_name):
        geometry_options = {
            "paper": paper_size,
            "margin": ".5in",
        }
        if orientation == "landscape":
            geometry_options["landscape"] = True

        doc = Document(geometry_options=geometry_options)
        doc.packages.append(Package("tcolorbox"))  # For text boxes
        doc.packages.append(Package("xcolor"))  # For color management
        # Define the tcolorbox style
        doc.preamble.append(
            NoEscape(
                r"""
\newtcolorbox{mytextbox}{
    colback=white,        % Background color
    colframe=black,       % Border color
    boxrule=0.5mm,        % Border thickness
    arc=4mm,              % Rounded corners
    auto outer arc,       % Automatically adjust corners
    width=0.8\textwidth,  % Box width (80% of text width)
    before skip=10pt,     % Space before the box
    after skip=10pt,      % Space after the box
    boxsep=5pt,           % Separation between frame and content
    left=5pt,             % Left padding
    right=5pt,            % Right padding
    top=5pt,              % Top padding
    bottom=5pt,           % Bottom padding
    title=Details,        % Optional: Title of the box
    fonttitle=\bfseries,  % Optional: Title font style
    coltitle=black        % Optional: Title color
}
"""
            )
        )
        doc.preamble.append(NoEscape(r"\definecolor{darkmode}{HTML}{2C3E50}"))
        doc.preamble.append(
            Command("title", "{%s} Inventory Label" % item_name)
        )
        doc.preamble.append(
            NoEscape(r"\pagecolor{darkmode}")
        )  # Example: Light grey background
        doc.preamble.append(NoEscape(r"\color{white}"))
        doc.preamble.append(NoEscape(r"\setlength{\headheight}{80pt}"))
        doc.preamble.append(NoEscape(r"\setlength{\headsep}{20pt}"))
        return doc

    def add_header(self, doc, logo_path, barcode_path, qr_path):
        header = PageStyle("header")
        with header.create(Head("L")) as left_header:
            with left_header.create(
                MiniPage(width=NoEscape(r"0.3\textwidth"), pos="c")
            ) as logo_wrapper:
                logo_wrapper.append(
                    StandAloneGraphic(
                        image_options="width=100px", filename=logo_path
                    )
                )
        with header.create(Head("R")) as right_header:
            with right_header.create(
                MiniPage(width=NoEscape(r"\textwidth"), pos="c")
            ) as image_wrapper:
                # the following aligns this header to the right of the display
                image_wrapper.append(NoEscape(r"\begin{flushright}"))

                # Add Barcode image
                image_wrapper.append(
                    StandAloneGraphic(
                        image_options="height=100px", filename=barcode_path
                    )
                )

                # Add horizontal space between images
                image_wrapper.append(NoEscape(r"\hspace{10pt}"))

                # Add QR Code, raisebox adds vertical padding from the bottom
                # so that it aligns with barcode
                image_wrapper.append(
                    NoEscape(
                        r"\raisebox{8mm}{\includegraphics[width=80px]{%s}}"
                        % qr_path
                    )
                )

                image_wrapper.append(NoEscape(r"\end{flushright}"))
        doc.preamble.append(header)
        doc.change_document_style("header")

    def add_product_details(self, doc, details):
        with doc.create(Section("Product Details", numbering=False)):
            for key, value in details.items():
                with doc.create(
                    Subsection(
                        NoEscape(r"\textbf{%s}" % key.capitalize()),
                        numbering=False,
                    )
                ):
                    doc.append(value)

    def add_images(self, doc, barcode_io, qr_code_io):
        with doc.create(
            MiniPage(width=NoEscape(r"\textwidth"), pos="t")
        ) as image_wrapper:
            image_wrapper.append(NoEscape(r"\begin{flushright}"))
            # Add Barcode
            image_wrapper.append(
                StandAloneGraphic(image_options="", filename=barcode_io)
            )
            # Add QR Code
            image_wrapper.append(
                StandAloneGraphic(image_options="", filename=qr_code_io)
            )
            image_wrapper.append(NoEscape(r"\end{flushright}"))

    def add_text_box(self, doc, hazards, precautions):
        """
        Adds a large, centered text box to the document containing items from a list.

        :param doc: The PyLaTeX Document object.
        :param items_list: A list of strings to include in the text box.
        """
        # Begin the tcolorbox environment
        doc.append(NoEscape(r"\begin{mytextbox}"))

        # Optional: Add a subtitle or additional formatting inside the box
        # doc.append(NoEscape(r"\textbf{Additional Information:}"))

        # Begin an itemize environment for listing items
        doc.append(NoEscape(r"\begin{itemize}"))

        for item in hazards:
            # Add each item as a bullet point
            doc.append(NoEscape(r"\item " + item + "\par"))

        for item in precautions:
            doc.append(NoEscape(r"\item " + item + "\par"))

        # End the itemize environment
        doc.append(NoEscape(r"\end{itemize}"))

        # End the tcolorbox environment
        doc.append(NoEscape(r"\end{mytextbox}"))

    def generate_pdf(self, details, hazards, precautions):

        item_name = details.get("name")
        volume = details.get("volume")
        concentration = details.get("concentration")

        printed_details = {
            "Item Name": item_name,
            "Volume": volume,
            "Concentration": concentration,
        }

        barcode_input = details.get("barcode_input")
        qr_code_input = details.get("qr_code_input")

        
        orientation = details.get("page_size")
        print(orientation)
        orientation = "landscape" if orientation == "Landscape" else "portrait"
        
        print(f"Printed details: {printed_details} | Barcode Input: {barcode_input} | Qr_Code: {qr_code_input} | Orientation: {orientation}")
        selected_hazards = self.selected_items(hazards)
        selected_precautions = self.selected_items(precautions)

        documentTitle = f"{item_name} Inventory Label"

        # image paths found in the AppConfig class
        logo_path = AppConfig.SOFAB_LOGO
        flame_path = AppConfig.FLAME

        barcode_filename = self.generate_barcode(barcode_input)
        qr_code_filename = self.generate_qr_code(qr_code_input)

        doc = self.create_document(orientation, "a4paper", item_name)

        self.add_header(doc, logo_path, barcode_filename, qr_code_filename)
        self.add_product_details(doc, printed_details)
        self.add_text_box(doc, selected_hazards, selected_precautions)
        doc.generate_pdf("output", clean_tex=False)

    def selected_items(self, item_list):
        selected_items = []
        if item_list is not None:
            for var, label in item_list:
                if var.get():
                    selected_items.append(label)
        return selected_items
