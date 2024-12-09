import math
import tkinter as tk
from tkinter import Tk, filedialog, messagebox, ttk

import customtkinter
from views.CTkXYFrame import *
from views.CTkMessagebox import *
from PIL import Image, ImageGrab, ImageTk

from config import AppConfig
from reportlab.lib.pagesizes import A4, landscape

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from barcode import Code128
import qrcode
from barcode.writer import ImageWriter
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from pdf_generator2 import PDFGenerator

from views.widgets import *

from tkinter import Toplevel
from pdfcreator import PDFCreator


# from ttkbootstrap import Style

# from views.item_frame import ItemFrameContainer
# from views.submission_frame import SubmitFrame
# from views.warning_frame import HazardPrecautionFrame


# New Label Print GUI!
class MyApp2(customtkinter.CTk):
    def __init__(self, controller):
        super().__init__()

        self.controller = controller
        self.controller.set_view(self)
        self.pdf_generator = PDFGenerator
        self.popup_open = False

        self.table_types = self.controller.get_item_type_tables()

        
        self.table_keys = {
            "chemical_inventory": [key for key in self.table_types if "chemical inventory" in key.lower()],
            "general_inventory": [key for key in self.table_types if "general" in key.lower()],
            "product": [key for key in self.table_types if "product" in key.lower()],
            #"chem_details": [key for key in self.table_types if "details" in key.lower()]
        }

        #Sensitive - Move somewhere else
        self.default_address = "11351 Decimal Drive Louisville, KY 40299"
    
        self.area_1_frames = []

        self.tab_buttons = {}

        self.preview_key_details = {}

        self.selected_inventory_type = ""


        #Get latest id from chosen inventory type
        self.inventory_type = ''.join(self.table_keys["chemical_inventory"]).lower()

        
        # tab_name = self.inventory_type.replace(" ","_")
        # fetched_id = self.controller.next_id_str(self.controller.next_id(self.inventory_type))

        # self.controller.set_id_info(tab_name,fetched_id)
        # self.controller.set_new_barcode(self.controller.get_id_info()[tab_name])

        # Topbar - Chemical/General/Details Inventory and Submit
        self.setup_menu()
        
        # Dark mode
        customtkinter.set_appearance_mode("dark")

        #Configure window grid columns 
        self.configure_window_grid()
        
        # Create initial window and frame
        self.geometry("1400x840")
        self.window_frame = CTkXYFrame(self)
        self.window_frame.grid(row=1, column=0, sticky="nsew")

        # Configure grid expansion
        self.grid_rowconfigure(1, weight=15, uniform="equal")
        self.grid_columnconfigure(1, weight=0, uniform="equal")


        self.load_default_areas()


    def configure_window_grid(self):
        for row in range(1, 5):  # Rows 1 to 4 with weight=1
            self.grid_rowconfigure(row, weight=1)

        self.grid_rowconfigure(0, weight=0)  # Row 0 with weight=0

        # Configure columns
        for col in range(2):  # Columns 0 and 1 with weight=1
            self.grid_columnconfigure(col, weight=1)
    
    
    def setup_menu(self):
        self.topbar_frame = customtkinter.CTkFrame(
            self, height=60, corner_radius=0
        )
        self.topbar_frame.grid(row=0, column=0, columnspan=2, sticky="nsew")

        #Topbar - SoFab Logo!
        self.logo_photo = customtkinter.CTkImage(dark_image=Image.open(AppConfig.SOFAB_LOGO), size=(160,40))
        self.logo_label = customtkinter.CTkLabel(self.topbar_frame, image=self.logo_photo, text="")  # Empty text for the image
        self.logo_label.grid(row=0, column=0, padx=10, pady=15)
    
        #Topbar - Menu buttons - Removed
        #last_column = self.initialize_tab_buttons(self.table_types)

        #Topbar - Submit
        self.submit_button = customtkinter.CTkButton(
            self.topbar_frame, 
            text="Submit", 
            command=lambda: self.on_submit(),
            fg_color="transparent",
            border_width=0,
            font=customtkinter.CTkFont(size=14,weight="bold"),
        )
        self.submit_button.grid(row=0, column=1, padx=10, sticky="ns")
    
    #Chemical Inventory, General Inventory, Batch Inventory, Chemical Details, Submit
    def initialize_tab_buttons(self,table):
        tab_column_index = 1
        for i, name in enumerate(table):
            topbar_button = customtkinter.CTkButton(
                self.topbar_frame,
                text="Chemical Inventory" if "details" in name.lower() else name,
                command=lambda name=name: self.switch_tab(name),
                fg_color="transparent",
                border_width=0,
            )
            topbar_button.grid(row=0, column=1+tab_column_index, padx=10, pady=20)
            self.tab_buttons[name] = topbar_button
            tab_column_index += 1
        return tab_column_index
    

    def load_default_areas(self):
        
        # Load warning dictionaries
        hazard_warnings = self.controller.get_hazard_classes_dict()
        precaution_warnings = self.controller.get_precaution_classes_dict()
        hazard_diamonds = self.controller.get_hazard_diamonds_dict()
        self.stored_preview_text = ""
        self.stored_diamonds = []

        # Contains print textbox to display selected warning items
        #self.area_5 = WarningPrintFrame(self.window_frame, self.controller)
        #self.area_5.grid(row=2, column=1, columnspan=2, sticky="nsew", padx=10, pady=10)

        # Choose inventory type
        #self.area_0 = customtkinter.CTkFrame(self.window_frame,height=20)
        #self.area_0.place(x=10, y=10, relwidth=0.6)
        #self.area_0.grid(row=1, column=0,sticky="ew", padx=10, pady=10)
        #self.window_frame.grid_rowconfigure(0, weight=0)

        # Key Chemical Details
        self.area_1 = DetailSelectFrame(self.window_frame,self.controller,self.table_keys["chemical_inventory"],self)
        self.area_1.configure(corner_radius=10)
        self.area_1.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        #self.initialize_tab_dropdown(self.table_types)

        # Contains hazards and precautions
        self.area_2 = WarningSelectFrame(self.window_frame, self.controller, hazard_warnings, precaution_warnings, root=self)
        self.area_2.configure(corner_radius=10)
        self.area_2.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)

        # Create hazard symbols frame
        self.area_3 = HazardSymbolFrame(self.window_frame,self.controller, hazard_diamonds, root=self)
        self.area_3.configure(corner_radius=10)
        self.area_3.grid(row=3, column=0, sticky="nsew", padx=10, pady=10)

        
        # Contains Preview box and orientation selection
        self.area_4 = PreviewFrame(self.window_frame, self.controller, root=self)
        self.area_4.configure(corner_radius=10)
        self.area_4.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
    
    # Creates general info labels
    def label_tables(self, key, i):
        table_label_text = f"{self.format_names(key)} \n    Information"

        self.table_label = customtkinter.CTkLabel(
            self.area_1,
            text=table_label_text,
        )
        self.table_label.grid(row=0, column=i)
        return table_label_text

    # Ex: chemical_inventory -> Chemical Inventory
    def format_names(self, names):
        if type(names) is list:
            return [name.replace("_", " ").title() for name in names]
        elif type(names) is str:
            return names.replace("_", " ").title()

    # Switch between Chemical/General Inventory
    def switch_tab(self, button_name):
        #Refresh areas - Keep preview visible
        inventory_map = {
        "chemical inventory": "Chemical Inventory",
        "general inventory": "General Inventory",
        #"chemical details": "Chemical Details",
        "batch inventory": "Batch Inventory",
        "product": "Product Inventory (Batch Process)"
        }

        button_name_lower = button_name.lower()

        for key, value in inventory_map.items():
            if key in button_name_lower:
                self.inventory_type = value.lower()
                self.update_area_layout(value)
                self.create_area_frame(value)
                self.controller.clear_data_entries()
                self.area_4.switch_preview_box()
                break
        
        #Refresh preview label
        
        
        
    def update_area_layout(self, area_to_show):
        # Reset all areas
        self.area_2.grid_forget()
        self.area_3.grid_forget()
        #self.area_5.grid_forget()

        # Apply layout for the selected area
        if area_to_show == "Chemical Inventory": #or area_to_show == "Chemical Details":
            self.area_2.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
            self.area_3.grid(row=3, column=0, sticky="nsew", padx=10, pady=10)
            #self.area_5.grid(row=2, column=1, columnspan=2, sticky="nsew", padx=10, pady=10)

    def create_area_frame(self, inventory_type):
        # Mapping between inventory type and corresponding table key
        area_mappings = {
            "Chemical Inventory": self.table_keys["chemical_inventory"],
            "General Inventory": self.table_keys["general_inventory"],
            #"Chemical Details": self.table_keys["chem_details"],
            "Product Inventory": self.table_keys["product"]
        }

        for key, value in area_mappings.items():
            if key.lower() in inventory_type.lower():  # Check if part of inventory_type matches key
                self.area_1 = DetailSelectFrame(self.window_frame, self.controller, value[0], self)
                self.area_1.configure(corner_radius=10)
                self.area_1.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
                break

    #When add to database is toggled
    def checkbox_changed(self):
        if self.area_1.add_to_db_var.get() == "on":
            #Force entry check
            self.area_1.update_entries(False)
            self.controller.set_db_insertion(True)
            
        else:
            self.controller.set_db_insertion(False)

    def on_submit(self):

        self.controller.on_submission2()

        #messagebox.showinfo("", "Label generated successfully")
        self.update_barcode_qr()
        
        # Create png, convert to pdf

        self.close_popup()
        self.create_print_popup()
        #self.pdf_generator = PDFGenerator(preview,preview.winfo_children())
        #self.pdf_generator.save_to_pdf2()
        #self.pdf_generator.export_to_pdf_custom(self,preview,preview.winfo_children())
        #self.data_process_message("PDF created successfully!")

        #Refresh Entry boxes
        # for box in self.area_1.entry_vars.values():
        #     box.delete(0, tk.END)
        
        # self.area_1.disable_details_checkboxes()
        # self.area_4.update_frame("Landscape")
    
    
    def create_print_popup(self):
        # Create a new top-level window (popup)
        self.popup = Toplevel(self.window_frame)
        self.popup.title("Popup Window")
        self.popup.geometry("1200x630")

        #self.print_frame = customtkinter.CTkFrame(self.popup, corner_radius=0)
        #self.print_frame.pack(fill="both", expand=True)  # Center the frame on the popup

        # Choose label size, export to PDF
        preview = self.area_4.preview_label_frame
        print_options_frame = PDFCreator(self.popup,preview,preview.winfo_children(),self)
        print_options_frame.pack(fill="both", expand=True)
        print_options_frame.load_options()
        self.popup_open = True


    
    def close_popup(self):
        if self.popup_open:
            self.popup.destroy()
            self.popup_open = False

    def update_barcode_qr(self):
        #Create new barcode
        self.generate_barcode(self.controller.get_new_barcode())
        self.area_4.barcode_photo_prev.configure(dark_image=Image.open(self.controller.get_barcode_image()))
        self.area_4.barcode_label_prev.configure(image=self.area_4.barcode_photo_prev)

        #Create new qr_code
        self.generate_qr_code(self.controller.get_qr_code_entry())
        new_qr_code = customtkinter.CTkImage(dark_image=Image.open(self.controller.get_qr_code_image()), size=(80,80))
        self.area_4.qr_code_label.configure(image=new_qr_code)

        #image_width = self.qr_code_image_preview.size[0]
        self.area_4.barcode_label_prev.grid(row=0, column=1, padx=0, sticky="w")
        self.area_4.qr_code_label.grid(row=0, column=2,padx=(0,5),sticky="e")
        #self.qr_code_label.grid(padx=(0,15))

    def generate_barcode(self,input_string):
        try:
            file_name = "barcode"
            my_code = Code128(input_string, writer=ImageWriter())
            my_code.save(file_name)  # Save the barcode as "barcode.png"
            self.controller.set_barcode_image(f"{file_name}.png")
            return f"{file_name}.png"  # Return the file path for later use
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return None
    
    def generate_qr_code(self,input_string):
        try:
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(input_string)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")
            file_name = "qr_code"
            img.save(f"{file_name}.png")
            self.controller.set_qr_code_image(f"{file_name}.png")
            return f"{file_name}.png"  # Return the file path for later use
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return None

    #Delete later
    def update_printbox(self):
        pass
    
    def data_error_message(self,err):
        CTkMessagebox(title="Error", message=err, icon="cancel")
        self.area_1.add_to_db_var.set(value="off")
    
    def data_process_message(self,mess):
        CTkMessagebox(title="Confirmation", message=mess, icon="check")
    
    def data_warning_message(self,mess):
        CTkMessagebox(title="Warning", message=mess, icon="warning")
                    
# if __name__ == "__main__":
# app = App()
# app.mainloop()
