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

    def on_submission(self):
        batch = self.view.chemical_frame.batch_entry.get()
        #    size = size_entry.get()
        date = self.view.chemical_frame.date_entry.get()
        volume = self.view.chemical_frame.volume_entry.get()
        concentration = self.view.chemical_frame.concentration_entry.get()
        barcode_input = self.view.chemical_frame.barcode_entry.get()
        qr_code_input = self.view.chemical_frame.qr_code_entry.get()
        page_size_option = self.view.chemical_frame.page_size_var.get()
        stage = self.view.chemical_frame.stage_choice.get()

        selected_hazards = self.get_selected_hazards(hazard=True)
        selected_precautions = self.get_selected_hazards(precautions=True)

        barcode_input = self.view.chemical_frame.barcode_entry.get()
        barcode_path = PDF_generator.generate_barcode(barcode_input)

        qr_code_input = self.view.chemical_fram.qr_code_entry.get()
        qr_path = self.pdf_generator.generate_qr_code(qr_code_input)

        ## Add barcode batch id to database
        # print_synthesis_rows(barcode_input.upper(), stage)

        ## Set page size based on user selection
        # page_size = landscape(A4) if page_size_option == "Landscape" else A4

        # generate_pdf(
        #    batch,
        #    date,
        #    concentration,
        #    volume,
        #    barcode_path,
        #    qr_code_path,
        #    page_size,
        #    text,
        # )

        self.pdf_generator.generate_pdf()

        print(
            batch,
            date,
            volume,
            concentration,
            barcode_input,
            qr_code_input,
            page_size_option,
            stage,
            selected_hazards,
            selected_precautions,
        )

        # messagebox.showinfo("Success", "PDF generated successfully!")
