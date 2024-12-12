import customtkinter
import tkinter as tk
from tkinter import ttk

from PIL import Image, ImageTk
from reportlab.lib.pagesizes import A4, landscape
from config import AppConfig
from views.widgets2 import *

# Main Tab Screens
class ChemicalInventoryFrame(customtkinter.CTkFrame):
    def __init__(self, tab, controller,tables):
        super().__init__(tab)
        self.controller = controller

        print(f"Welcome to {tables}")

class GeneralInventoryFrame(customtkinter.CTkFrame):
    def __init__(self, tab, controller,tables):
        super().__init__(tab)
        self.controller = controller

        print(f"Welcome to {tables}")

class BatchInventoryFrame(customtkinter.CTkFrame):
    def __init__(self, tab, controller,tables):
        super().__init__(tab)
        self.controller = controller

        print(f"Welcome to {tables}")

        self.details = DetailSelectFrame(tab,self.controller,tables)
        self.details.pack(side="right",pady=10)


class ChemicalDetailsFrame(customtkinter.CTkFrame):
    def __init__(self, tab, controller,tables):
        super().__init__(tab)
        self.controller = controller

        print(f"Welcome to {tables}")
        
        self.details = DetailSelectFrame(tab,self.controller,tables)
        self.details.pack(side="left",pady=10)
