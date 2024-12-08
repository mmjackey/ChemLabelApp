import customtkinter
import tkinter as tk
from tkinter import ttk

from PIL import Image, ImageTk


class WarningPrintFrame(customtkinter.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        # Configure columns
        for col in range(4): self.grid_columnconfigure(col, weight=1)

        # Create header and textbox
        self.area_5_header = customtkinter.CTkLabel(self, text="Print", font=customtkinter.CTkFont(size=18, weight="bold"))
        self.area_5_header.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.text_box = customtkinter.CTkTextbox(self, height=100)
        self.text_box.grid(row=1, column=0, columnspan=2, padx=10, pady=(5, 10))
