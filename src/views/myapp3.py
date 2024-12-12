# Standard Library Imports
import math
import tkinter as tk
from tkinter import Tk, filedialog, messagebox, ttk

# Third-Party Imports
import customtkinter
from PIL import Image, ImageGrab, ImageTk
from reportlab.lib.pagesizes import A4, landscape, letter  # Combined imports
from reportlab.pdfgen import canvas
from barcode import Code128
from barcode.writer import ImageWriter
import qrcode
from reportlab.lib import colors

# Custom Module Imports
from views.CTkXYFrame import *
from views.CTkMessagebox import *
from config import AppConfig

# Custom widgets
from views.widgets import *
from views.inventory_tabs import *

# New Label Print GUI!
class MyApp3(customtkinter.CTk):

    def __init__(self, controller):
        super().__init__()

        self.controller = controller
        self.controller.set_view(self)

        # Fetch tables from db
        self.inventory_tables = self.controller.get_item_type_tables()

        # Chemical / General / Details Inventory
        self.tab_frames = {}
        self.tab_content_frame = customtkinter.CTkFrame(self)
        self.tab_content_frame.pack(side="bottom", fill="both", expand=True)

        print(list(self.inventory_tables))

        self.setup_menu()

        self.set_tabs(self.tab_content_frame)
        
        # Dark mode
        customtkinter.set_appearance_mode("dark")

        self.switch_tab(self.inventory_tables.popitem()[0])

        self.configure_window_grid()

    def setup_menu(self):
        # Topbar Menu
        self.topbar_frame = customtkinter.CTkFrame(
            self, height=60, corner_radius=0
        )
        self.topbar_frame.pack(fill="x", expand=False)

        # Menu Buttons
        for tab_name, content in self.inventory_tables.items():
            topbar_button = customtkinter.CTkButton(
                self.topbar_frame,
                text=tab_name,
                command=lambda name=tab_name: self.switch_tab(name),
                fg_color="transparent",
                border_width=0,
            )
            topbar_button.pack(side="left", padx=5, pady=5)
    
    def set_tabs(self,tabview : customtkinter.CTkFrame):
        tab_name = list(self.inventory_tables)[0]
        tab_frame1 = ChemicalInventoryFrame(
            tabview, self.controller, list(self.inventory_tables.values())[0]
        )  
        tab_frame1.pack(fill="both", expand=True)
        self.tab_frames[tab_name] = tab_frame1

        tab_name = list(self.inventory_tables)[1]
        tab_frame2 = GeneralInventoryFrame(
            tabview, self.controller, list(self.inventory_tables.values())[1]
        )
        tab_frame2.pack(fill="both", expand=True)
        self.tab_frames[tab_name] = tab_frame2

        tab_name = list(self.inventory_tables)[2]
        tab_frame3 = BatchInventoryFrame(
            tabview, self.controller, list(self.inventory_tables.values())[2]
        )
        tab_frame3.pack(fill="both", expand=True)
        self.tab_frames[tab_name] = tab_frame3

        tab_name = list(self.inventory_tables)[3]
        tab_frame4 = ChemicalDetailsFrame(
            tabview, self.controller, list(self.inventory_tables.values())[3]
        )
        tab_frame4.pack(fill="both", expand=True)
        self.tab_frames[tab_name] = tab_frame4

    def configure_window_grid(self):
        for row in range(1, 5):  # Rows 1 to 4 with weight=1
            self.grid_rowconfigure(row, weight=1)

        self.grid_rowconfigure(0, weight=0)  # Row 0 with weight=0

        # Configure columns
        for col in range(2):  # Columns 0 and 1 with weight=1
            self.grid_columnconfigure(col, weight=1)
    
        
    def switch_tab(self, tab_name):
        for frame in self.tab_frames.values():
            frame.pack_forget()
        self.tab_frames[tab_name].pack(fill="both", expand=True)
        print(tab_name)
    

       