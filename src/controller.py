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

    def send_hazards(self, hazard_type):
        return self.hazard_precautions_data.HAZARD_CLASSES.get(hazard_type, [])

    def get_selected_hazards(self, hazard=False, precautions=False):
        if hazard:
            return self.hazard_precautions_data.selected_hazards
        elif precautions:
            return self.hazard_precautions_data.selected_precautions
        else:
            return None

    def append_selected_hazard(self, var, hazard):
        self.hazard_precautions_data.selected_hazards.append((var, hazard))
