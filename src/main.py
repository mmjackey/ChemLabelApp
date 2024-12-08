from controller import Controller
from entry_parser import EntryParser
from models.database import Database
#from models.database2 import Database
from models.hazard_data import HazardsPrecautionData
from models.pdf_generator import PDFGenerator
#from views.app import App
#from views.myapp import MyApp
from views.myapp2 import MyApp2
#from views.myapp3 import MyApp3
from entry_parser import EntryParser


def main():

    database_model = Database()
    pdf_generator = PDFGenerator()
    hazard_precaution_data = HazardsPrecautionData()
    entry_parser = EntryParser(database_model)

    controller = Controller(
        database_model, pdf_generator, hazard_precaution_data, entry_parser
    )

    # Old - App(controller)
    # New - MyApp(controller)
    app = MyApp2(controller)

    app.mainloop()


if __name__ == "__main__":
    main()
