import yaml
import os
import sys
from config import AppConfig


class HazardsPrecautionData:
    def __init__(self):
        self.selected_hazards = []
        self.selected_precautions = []
        self.diamond_vars = []
        self.hazard_data_file = self.get_path("src/models/hazard_data.yaml")

        with open(self.hazard_data_file, "r") as file:
            self.HAZARD_DATA = yaml.safe_load(file)

        self.HAZARD_CLASSES = self.HAZARD_DATA["HAZARD_CLASSES"]
        self.PRECAUTION_CLASSES = self.HAZARD_DATA["PRECAUTION_CLASSES"]

        self.HAZARD_DIAMONDS = {
            "Diamonds": [
                (name, AppConfig.HAZARD_IMAGES / filename)
                for name, filename in self.HAZARD_DATA[
                    "HAZARD_CLASSES_GENERAL"
                ].items()
            ]
        }

    def get_path(self, relative_path):
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    def add_hazard(self, hazard):
        self.selected_hazards.append(hazard)

    def add_precaution(self, hazard):
        self.selected_precautions.append(hazard)
