import customtkinter
import tkinter as tk
from tkinter import ttk

from PIL import Image, ImageTk
from views.hazardprecautionframe2 import HazardPrecautionFrame2
from views.hazardprecautionframe2 import WarningClassCheckboxes

class WarningSelectFrame(customtkinter.CTkFrame):
    def __init__(self, parent, controller, hazards,precautions, root):
        super().__init__(parent)

        self.root = root
        self.parent = parent
        self.controller = controller

        # Make columns expandable
        for col in range(4):
            self.grid_columnconfigure(col, weight=1)

        # Create hazard frame
        self.create_header(self, "Hazard Details", 0)
        self.hazard_frame = self.create_frame(self, hazards, 1, hazard_print=self.root.area_5.text_box)  # Add appropriate hazard_print value

        # Create precautionary frame
        self.create_header(self, "Precautionary Details", 2)
        self.precautions_frame = self.create_frame(self, precautions, 3,hazard_print=self.root.area_5.text_box)


    # Helper function to create header labels
    def create_header(self, parent, text, row):
        header = customtkinter.CTkLabel(
            parent,
            text=text,
            font=customtkinter.CTkFont(size=18, weight="bold"),
        )
        header.grid(row=row, column=0, padx=10, pady=10, sticky="w")
        return header

    # Helper function to create frames
    def create_frame(self, parent, warning_dict, row, hazard_print=None):
        frame = HazardPrecautionFrame2(
            parent,
            controller=self.controller,
            warning_dict=warning_dict,
            root=self.root,
            images=False,
            hazard_print=hazard_print
        )
        frame.grid(row=row, column=0, columnspan=4, padx=10, pady=10, sticky="ew")
        frame.grid_columnconfigure(4, weight=1)
        return frame

class HazardSymbolFrame(customtkinter.CTkFrame):
    def __init__(self, parent, controller, diamonds, root, hazard_print=None):
        super().__init__(parent)    
        
        self.root = root
        self.parent = parent
        for col in range(4):  # Configure first 4 columns with weight=1
            self.grid_columnconfigure(col, weight=1)

        self.area_3_header = customtkinter.CTkLabel(
            self,
            text="Hazard Symbols",
            font=customtkinter.CTkFont(size=18, weight="bold"),
        )
        self.area_3_header.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.hazard_diamonds_frame = HazardPrecautionFrame2(
            self,
            controller,
            warning_dict=diamonds,
            root=self.root,
            images=True,
            hazard_print=hazard_print,
        )
        self.hazard_diamonds_frame.grid(
            row=1, column=0, columnspan=4, padx=10, pady=10, sticky="ew"
        )

        self.hazard_diamonds_frame.grid_columnconfigure(4, weight=1)

                
