from models.database import Database
from models.hazard_data import Hazards_precaution_data
from models.pdf_generator import PDF_generator


class Controller:
    def __init__(self, view):
        self.view = view

        self.database = Database()
        self.pdf_generator = PDF_generator()
        self.hazard_precautions_data = Hazards_precaution_data()

        self.view.set_callbacks(self)

    def handle_submit_pdf(self):
        pass

    def get_hazards(self, hazard_type):
        return self.hazard_precautions_data.HAZARD_CLASSES.get(hazard_type, [])

    def get_selected_hazards(self):
        return self.hazard_precautions_data.selected_hazards

    def append_hazard_variables(self, var, hazard):
        self.hazard_precautions_data.selected_hazards.append((var, hazard))

    def get_selected_precautions(self):
        return self.hazard_precautions_data.selected_precautions

    def append_precautions_variables(self, var, precaution):
        self.hazard_precautions_data.selected_precautions.append(
            (var, precaution)
        )

    def get_precautions(self, precaution_type):
        return self.hazard_precautions_data.PRECAUTION_CLASSES.get(
            precaution_type, []
        )

    def on_submission(self):
        details = self.view.chemical_frame.get_item_details()

        # selected_hazards = self.get_selected_hazards()
        # selected_precautions = self.get_selected_precautions()

        ## Add barcode batch id to database
        # print_synthesis_rows(barcode_input.upper(), stage)

        ## Set page size based on user selection
        # page_size = landscape(A4) if page_size_option == "Landscape" else A4

        self.pdf_generator.generate_pdf(details)

        # messagebox.showinfo("Success", "PDF generated successfully!")
