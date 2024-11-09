from controller import Controller
from models.database import Database
from models.hazard_data import HazardsPrecautionData
from models.pdf_generator import PDFGenerator
from views.app import App


def main():

    database_model = Database()
    pdf_generator = PDFGenerator()
    hazard_precaution_data = HazardsPrecautionData()

    controller = Controller(
        database_model, pdf_generator, hazard_precaution_data
    )

    app = App(controller)

    app.mainloop()


if __name__ == "__main__":
    main()
