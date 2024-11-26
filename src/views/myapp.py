import math
import tkinter as tk
from tkinter import Tk, filedialog, messagebox, ttk

import customtkinter
from views.CTkXYFrame import *
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

# from ttkbootstrap import Style

# from views.item_frame import ItemFrameContainer
# from views.submission_frame import SubmitFrame
# from views.warning_frame import HazardPrecautionFrame


# New Label Print GUI!
class MyApp(customtkinter.CTk):
    def __init__(self, controller):
        super().__init__()

        self.controller = controller
        self.controller.set_view(self)

        #Load table information
        item_type_tables = self.controller.get_item_type_tables()
        self.table_types = item_type_tables

        #Get chemical inventory table
        self.chem_inventory_keys = [key for key in self.table_types if "chemical inventory" in key.lower()]
        
        #Get general inventory table
        self.gen_inventory_keys = [key for key in self.table_types if "general" in key.lower()]

        #Get batch process table
        self.product_keys = [key for key in self.table_types if "product" in key.lower()]


        #Get chem details table
        self.chem_details = [key for key in self.table_types if "details" in key.lower()]

        print(self.chem_details)
        self.default_address = "11351 Decimal Drive Louisville, KY 40299"
    
        self.area_1_frames = []

        #See if table exists
        #print(self.product_keys)

        
        # Load warning dictionaries
        hazard_warnings = self.controller.get_hazard_classes_dict()
        precaution_warnings = self.controller.get_precaution_classes_dict()
        hazard_diamonds = self.controller.get_hazard_diamonds_dict()

        self.item_type_frames = {}
        self.tab_buttons = []
        self.preview_key_details = {}

        # Make window rows and columns expandable
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self.grid_rowconfigure(4, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Topbar - Chemical/General Inventory and Submit
        self.topbar_frame = customtkinter.CTkFrame(
            self, height=60, corner_radius=0
        )
        self.topbar_frame.grid(row=0, column=0, columnspan=2, sticky="nsew")

        #SOFAB LOGO
        #Load images
        self.logo_image = Image.open("resources\images\sofab_logo.png")
        self.logo_image2 = Image.open("resources/images/sofab_logo2.png")
        self.logo_image3 = Image.open("resources/images/speed-school.png")
        self.logo_photo = customtkinter.CTkImage(dark_image=self.logo_image, size=(160,40))
        self.logo_label = customtkinter.CTkLabel(self.topbar_frame, image=self.logo_photo, text="")  # Empty text for the image
        self.logo_label.grid(row=0, column=0, padx=10, pady=10)

        tab_column_index = 1
        for i, name in enumerate(self.table_types):
            if "product" in name.lower():
                continue
            topbar_button = customtkinter.CTkButton(
                self.topbar_frame,
                text="Chemical Details" if "details" in name.lower() else name,
                command=lambda name=name: self.sidebar_button_event(name),
                fg_color="transparent",
                border_width=0,
            )
            topbar_button.grid(row=0, column=1+tab_column_index, padx=10, pady=10)
            self.tab_buttons.append(topbar_button)
            tab_column_index += 1
        # self.topbar_button_1 = customtkinter.CTkButton(
        #     self.topbar_frame,
        #     text="Chemical Details",
        #     command=lambda: self.sidebar_button_event("Chemical Details"),
        #     fg_color="transparent",
        #     border_width=0,
        # )
        # self.topbar_button_1.grid(row=0, column=2, padx=10, pady=10)

        # self.topbar_button_2 = customtkinter.CTkButton(
        #     self.topbar_frame,
        #     text="Chemical Inventory",
        #     command=lambda: self.sidebar_button_event("Chemical Inventory"),
        #     fg_color="transparent",
        #     border_width=0,
        # )
        # self.topbar_button_2.grid(row=0, column=3, padx=10, pady=10)

        # self.topbar_button_3 = customtkinter.CTkButton(
        #     self.topbar_frame,
        #     text="General Inventory",
        #     command=lambda: self.sidebar_button_event("General Inventory"),
        #     fg_color="transparent",
        #     border_width=0,
        # )
        # self.topbar_button_3.grid(row=0, column=4, padx=10, pady=10)

        # Sumbit to PDF (Not functional)
        self.submit_button = customtkinter.CTkButton(
            self.topbar_frame, 
            text="Submit", 
            command=lambda: self.on_submit(),
            fg_color="transparent",
            border_width=0,
        )
        self.submit_button.grid(row=0, column=tab_column_index+1, padx=10, pady=10)
        
        customtkinter.set_appearance_mode("dark")

        # Create initial window
        self.geometry("1400x840")
        self.window_frame = CTkXYFrame(
            self
        )
        self.window_frame.grid(
            row=1, column=0, sticky="nsew"
        )  # Sticky to fill the whole window

        # Ensure the grid expands in both row and column
        self.grid_rowconfigure(
            1, weight=15, uniform="equal"
        )  # Row 0 will take all vertical space
        self.grid_columnconfigure(
            1, weight=0, uniform="equal"
        )  # Column 0 will take all horizontal space

        # Set Default areas
        # Contains print textbox to display selected warning items
        self.create_area_5()

        # Key Chemical Details
        self.inventory_type = ''.join(self.chem_details).lower()
        self.create_area_1(self.chem_details)

        # Contains hazards and precautions
        self.create_area_2(
            self.controller, hazard_warnings, precaution_warnings
        )

        # Contains hazard diamond symbols
        self.create_area_3(self.controller, hazard_diamonds)

        self.stored_preview_text = ""
        self.stored_diamonds = []
        # Contains Preview box and orientation selection
        self.create_area_4()

    # First area - Fill in key chemical/general inventory details
    def create_area_1(self, table):

        #Get latest id from chosen inventory type
        self.controller.set_id_info(self.inventory_type.replace(" ","_"),self.controller.next_id(self.controller.database.get_latest_barcode_id(self.inventory_type)))
        self.controller.set_new_barcode(self.controller.get_id_info()[self.inventory_type.replace(" ","_")])

        table_columns_dict = self.controller.get_database_column_names(
            self.table_types[''.join(table)]
        )
        #print(table_columns_dict)

        #Current tab is accessible from controller class
        if table_columns_dict:
            self.controller.set_tab(''.join(table))
            
        #print(self.controller.get_tab_info())

        #Store all EntryBox widgets
        self.entry_vars = {}

        # *Important* - Store entrybox values (when they change)
        #self.area_1_entries = {}

        #Other

        for widget in self.area_1_frames:
            widget.destroy()
        self.area_1 = customtkinter.CTkFrame(self.window_frame, corner_radius=10)
        self.area_1.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        self.area_1_frames.append(self.area_1)

        # Make columns expandable
        
        self.area_1.grid_columnconfigure(0, weight=1)  # Label
        self.area_1.grid_columnconfigure(1, weight=1)  # Entry
        self.area_1.grid_columnconfigure(2, weight=1)  # Empty
        self.area_1.grid_columnconfigure(3, weight=1)  # Empty
        self.area_1.grid_columnconfigure(4, weight=1)  # Empty
        self.area_1.grid_columnconfigure(5, weight=1)  # Empty

        self.area_1_header = customtkinter.CTkLabel(
            self.area_1,
            text=''.join(table),
            font=customtkinter.CTkFont(size=18, weight="bold"),
        )
        self.area_1_header.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        #print(f"Header placed Row: {0} | Col: {0}")
        max_rows_per_column = 7
        row = 1 
        col = 0
        entry_count = 0
        self.entry_strings = []
        for i, (key, column_list) in enumerate(table_columns_dict.items()):
            # table_label_text = self.label_tables(key, i)
            formatted_table_columns = self.format_names(column_list)
            if "Product Inventory" in table:
                if "synthesis" not in key:
                    continue
            for j, column in enumerate(column_list):
                # print(j," ",column)
                if "id" in column.lower() or "hazard" in column.lower():
                    continue
                elif "quantity" in column.lower():
                    words = column.lower().split("_")
                    formatted_table_columns[j] = words[0].title()
                elif (
                    "fk" in column.lower()
                ):  # Change fk_location_general_inventory to 'Location'
                    words = column.lower().split("_")
                    words.remove("fk")
                    # for word in words:
                    # if word in table_label_text.lower():
                    # words.remove(word)
                    formatted_table_columns[j] = words[0].title()
                
                # Create the label for the column
                label = customtkinter.CTkLabel(
                    self.area_1, text=formatted_table_columns[j]
                )
                label.grid(row=row, column=col, padx=10, pady=5, sticky="ew")
                # print(formatted_table_columns[j],f"Label Placed Row: {row} | Col: {col}")
                if row == max_rows_per_column - 1:
                    label.grid(row=row, column=col, padx=20, pady=5)
                
                sv = customtkinter.StringVar()

                self.entry_strings.append(sv)
                sv.trace("w", lambda *args, name=formatted_table_columns[j], index=entry_count: self.update_key_details(name,index))


                # Create the entry for the column
                entry = customtkinter.CTkEntry(self.area_1,textvariable=sv)

                #Insert default SDS
                if "qr" in formatted_table_columns[j].lower():
                    default_sds = "https://drive.google.com/file/d/1HfsqJG-goraXZHW8OwokIUNG_nVDM_Uz/view"
                    entry.insert(0,default_sds)
                    self.controller.set_qr_code_entry(default_sds)
                entry.grid(row=row, column=col+1, padx=10, pady=5, sticky="w")
                
                #print(formatted_table_columns[j],f"Entry Placed Row: {row} | Col: {col+1}")
                if row == max_rows_per_column - 1:
                    entry.grid(row=row, column=col + 1, padx=10, pady=5)

                # Store the entry widget in a dictionary (self.entry_vars)
                self.entry_vars[column] = entry

                row += 1
                entry_count += 1
                if row >= max_rows_per_column:
                    row = 1
                    col += 2 
        
        #Address Entry
        address_label = customtkinter.CTkLabel(
            self.area_1, text="Address:"
        )
        address_label.grid(row=row, column=col, padx=10, pady=5, sticky="ew")

        sv2 = customtkinter.StringVar()

        self.entry_strings.append(sv2)
        sv2.trace("w", lambda *args, name="address", index=entry_count: self.update_key_details(name,index))

        address_entry = customtkinter.CTkEntry(self.area_1,textvariable=sv2)
        address_entry.grid(row=row, column=col+1, padx=10, pady=5, sticky="w")
        self.entry_vars[column] = entry
        
        #ADD TO DATABASE
        self.add_to_db_var = customtkinter.StringVar(value="off")
        self.db_insertion_checkbox = customtkinter.CTkCheckBox(
            self.area_1,
            text="Add to database",  # Label for the checkbox
            variable=self.add_to_db_var,  # Bind to the StringVar to track its state
            onvalue="on",  # The value when the checkbox is checked
            offvalue="off",  # The value when the checkbox is unchecked
            command=self.checkbox_changed  # Function to call when the state changes
        )
        self.db_insertion_checkbox.grid(row=max_rows_per_column+1, column=0, padx=10, pady=10, sticky="sw")
        #self.add_content()
    
    #Second area - Select warning items (hazards and precautions)
    def create_area_2(self, controller,hazards,precautions):
        self.area_2 = customtkinter.CTkFrame(self.window_frame, corner_radius=10)
        self.area_2.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)

        # Make columns expandable
        self.area_2.grid_columnconfigure(0, weight=1)  # Label
        self.area_2.grid_columnconfigure(1, weight=1)  # Entry
        self.area_2.grid_columnconfigure(2, weight=1)  # Empty
        self.area_2.grid_columnconfigure(3, weight=1)  # Empty

        # Create hazard frame
        self.area_2_header = customtkinter.CTkLabel(
            self.area_2,
            text="Hazard Details",
            font=customtkinter.CTkFont(size=18, weight="bold"),
        )
        self.area_2_header.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.hazard_frame = HazardPrecautionFrame(
            self.area_2,
            controller,
            warning_dict=hazards,
            root=self,
            images=False,
        )
        self.hazard_frame.grid(
            row=1, column=0, columnspan=4, padx=10, pady=10, sticky="ew"
        )
        self.hazard_frame.grid_columnconfigure(4, weight=1)

        # Create precautions frame
        self.area_2_header2 = customtkinter.CTkLabel(
            self.area_2,
            text="Precautionary Details",
            font=customtkinter.CTkFont(size=18, weight="bold"),
        )
        self.area_2_header2.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.precautions_frame = HazardPrecautionFrame(
            self.area_2,
            controller,
            warning_dict=precautions,
            root=self,
            images=False,
        )
        self.precautions_frame.grid(
            row=3, column=0, columnspan=4, padx=10, pady=10, sticky="ew"
        )
        self.precautions_frame.grid_columnconfigure(4, weight=1)

    # Third area - Choose hazard diamond symbols
    def create_area_3(self, controller, diamonds):
        self.area_3 = customtkinter.CTkFrame(
            self.window_frame, corner_radius=10
        )
        self.area_3.grid(row=3, column=0, sticky="nsew", padx=10, pady=10)

        # Make columns expandable
        self.area_3.grid_columnconfigure(0, weight=1)  # Label
        self.area_3.grid_columnconfigure(1, weight=1)  # Entry
        self.area_3.grid_columnconfigure(2, weight=1)  # Empty
        self.area_3.grid_columnconfigure(3, weight=1)  # Empty

        # Creae hazard diamonds frame
        self.area_3_header = customtkinter.CTkLabel(
            self.area_3,
            text="Hazard Symbols",
            font=customtkinter.CTkFont(size=18, weight="bold"),
        )
        self.area_3_header.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.hazard_diamonds_frame = HazardPrecautionFrame(
            self.area_3,
            controller,
            warning_dict=diamonds,
            root=self,
            images=True,
        )
        self.hazard_diamonds_frame.grid(
            row=1, column=0, columnspan=4, padx=10, pady=10, sticky="ew"
        )
        self.hazard_diamonds_frame.grid_columnconfigure(4, weight=1)

    # Fourth area - Preview label (choose orientation)
    def create_area_4(self):
        self.area_4 = customtkinter.CTkFrame(
            self.window_frame, corner_radius=10
        )
        self.area_4.grid(
            row=1, column=1, columnspan=2, sticky="nsew", padx=10, pady=10
        )

        # Make columns expandable
        self.area_4.grid_columnconfigure(0, weight=1)  # Label
        self.area_4.grid_columnconfigure(1, weight=1)  # Entry
        self.area_4.grid_columnconfigure(2, weight=1)  # Empty
        self.area_4.grid_columnconfigure(3, weight=1)  # Empty

        # Orientation Selection - Landscape or Portrait
        self.area_4_header = customtkinter.CTkLabel(
            self.area_4,
            text="Preview",
            font=customtkinter.CTkFont(size=18, weight="bold"),
        )
        self.area_4_header.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.orientation_option_menu = customtkinter.CTkOptionMenu(
            self.area_4,
            values=["Landscape", "Portrait"],
            command=self.update_frame,
        )
        self.orientation_option_menu.grid(
            row=1, column=0, sticky="nsew", padx=10, pady=10
        )

        #Preview Label frame 
        self.preview_label_frame = customtkinter.CTkFrame(self.area_4,fg_color="#FAF9F6",corner_radius=0)
        self.preview_label_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)

        # Set initial landscape preview
        self.update_frame(self.orientation_option_menu.get())

        #(self.orientation_option_menu.get())
    
    #Fifth area - Show Selected Warning Variables
    def create_area_5(self):
        self.area_5 = customtkinter.CTkFrame(
            self.window_frame, corner_radius=10
        )
        self.area_5.grid(
            row=2, column=1, columnspan=2, sticky="nsew", padx=10, pady=10
        )

        # Make columns expandable
        self.area_5.grid_columnconfigure(0, weight=1)  # Label
        self.area_5.grid_columnconfigure(1, weight=1)  # Entry
        self.area_5.grid_columnconfigure(2, weight=1)  # Empty
        self.area_5.grid_columnconfigure(3, weight=1)  # Empty

        # Create Print Textbox
        self.area_5_header = customtkinter.CTkLabel(
            self.area_5,
            text="Print",
            font=customtkinter.CTkFont(size=18, weight="bold"),
        )
        self.area_5_header.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.text_box = customtkinter.CTkTextbox(self.area_5, height=100)
        self.text_box.grid(
            row=1, column=0, columnspan=2, padx=10, pady=(5, 10)
        )

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
    def sidebar_button_event(self, button_name):
        #Refresh areas - Keep preview visible
        self.inventory_type = ""
        if button_name.lower() == ''.join(self.chem_inventory_keys).lower():
            self.inventory_type = ''.join(self.chem_inventory_keys).lower()
            self.area_2.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
            self.area_3.grid(row=3, column=0, sticky="nsew", padx=10, pady=10)
            self.area_5.grid(
            row=2, column=1, columnspan=2, sticky="nsew", padx=10, pady=10
            )
            self.create_area_1(self.chem_inventory_keys)
        if button_name.lower() == ''.join(self.gen_inventory_keys).lower():
            self.inventory_type = ''.join(self.gen_inventory_keys).lower()
            self.area_2.grid_forget()
            self.area_3.grid_forget()
            self.area_5.grid_forget()
            self.create_area_1(self.gen_inventory_keys)
        if button_name.lower() == ''.join(self.chem_details).lower():
            self.inventory_type = ''.join(self.chem_details).lower()
            self.area_2.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
            self.area_3.grid(row=3, column=0, sticky="nsew", padx=10, pady=10)
            self.area_5.grid(
            row=2, column=1, columnspan=2, sticky="nsew", padx=10, pady=10
            )
            self.create_area_1(self.chem_details)
        # if button_name.lower() == ''.join(self.product_keys).lower():
        #     self.inventory_type = "batch_inventory"
        #     self.area_2.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
        #     self.area_3.grid(row=3, column=0, sticky="nsew", padx=10, pady=10)
        #     self.area_5.grid(
        #     row=2, column=1, columnspan=2, sticky="nsew", padx=10, pady=10
        #     )
        #     self.create_area_1(self.product_keys)
        
        #Refresh preview label
        self.switch_preview_box()
    
    #When add to database is toggled
    def checkbox_changed(self):
        if self.add_to_db_var.get() == "on":
            self.controller.set_db_insertion(True)
        else:
            self.controller.set_db_insertion(False)


    def update_key_details(self, *args):
        

        #Load StringVar object
        entry_name = args[0]

        str_var = self.entry_strings[args[1]]
        
        #self.area_1_entries[entry_name] = str_var.get()
        self.controller.set_data_entries(entry_name,str_var.get())

        if "qr" in entry_name.lower():
            self.controller.set_qr_code_entry(str_var.get())
        
        # Do something with the updated value (for now, just print it)
        #print(f"Entry {args[0]} updated: {str_var.get()}")

        #Set preview text labels
        for key in self.preview_key_details.keys():
            for entry in self.controller.get_data_entries().keys():
                #print(f"Is {key.lower()} equal to {entry.lower()}?")
                if key.lower().replace("_"," ") in entry.lower():

                    if key.lower() == "address":
                        if not self.controller.get_data_entries()[entry]:
                            self.preview_key_details[key].configure(
                            text=str(f"{self.default_address}")
                            )
                        else:
                            self.preview_key_details[key].configure(
                            text=str(f"{self.controller.get_data_entries()[entry]}")
                            )
                        continue
                    new_key = key.replace("_"," ")
                    if "product" in new_key and self.controller.get_tab_info()[0] != "general_inventory":
                        new_key = "chemical name"
                    self.preview_key_details[key].configure(
                        text=str(f"{new_key.title()}: {self.controller.get_data_entries()[entry]}")
                    )
                if entry.lower() in key.lower().replace("_", " "):
                    new_key = entry.lower().replace("_"," ")
                    if "product" in new_key and self.controller.get_tab_info()[0] != "general_inventory":
                        new_key = "chemical name"
                    self.preview_key_details[key].configure(
                        text=str(f"{new_key.title()}: {self.controller.get_data_entries()[entry]}")
                    )


    #Not quite there yet
    def on_submit(self):
        for entry_field in self.entry_vars.keys():
            #print(f"{entry_field}: {self.entry_vars[entry_field].get()}")
            entry = self.entry_vars[entry_field].get()

        self.controller.on_submission2()
        #messagebox.showinfo("", "Label generated successfully")
        #Create new barcode
        self.generate_barcode(self.controller.get_new_barcode())
        self.barcode_photo_prev.configure(dark_image=Image.open(self.controller.get_barcode_image()))
        self.barcode_label_prev.configure(image=self.barcode_photo_prev)

        #Create new qr_code
        self.generate_qr_code(self.controller.get_qr_code_entry())
        self.qr_code_preview_photo.configure(dark_image=Image.open(self.controller.get_qr_code_image()))

        image_width = self.qr_code_image_preview.size[0]
        self.qr_code_label.configure(image=self.qr_code_preview_photo)
        self.barcode_label_prev.grid(row=0, column=1, padx=0, sticky="w")
        self.qr_code_label.grid(row=0, column=2,padx=(0,5),sticky="e")
        #self.qr_code_label.grid(padx=(0,15))
        
        
        self.capture_widget_as_image(self.preview_label_frame, "frame_capture.png")
        self.create_pdf("frame_capture.png", "label_output.pdf")
        
        
        print("PDF created successfully!")
    
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
    
    def capture_widget_as_image(self,widget, filename="widget_capture.png"):
        # Get the widget's bounding box
        x = widget.winfo_rootx()
        y = widget.winfo_rooty()
        width = widget.winfo_width()
        height = widget.winfo_height()

        img = ImageGrab.grab(bbox=(x, y, (x + width), (y + height)))
        new_image = img.rotate(-90)
        new_image = img.convert("RGB")
        

        new_image.save(filename)

    def create_pdf(self,image_path, pdf_filename="output.pdf"):
        page_width, page_height = landscape(A4)  # A4 landscape size (842.0 x 595.276)

        c = canvas.Canvas(pdf_filename, pagesize=(page_width, page_height))
        img = Image.open(image_path)
        
        img_width, img_height = img.size

        scale_factor = min(page_width / img_width, page_height / img_height)

        new_width = img_width * scale_factor
        new_height = img_height * scale_factor
        x_offset = (page_width - new_width) / 2
        y_offset = (page_height - new_height) / 2
        c.drawImage(image_path, x_offset, y_offset+20, width=new_width * 0.25, height=new_height * 0.25)
        c.drawImage(image_path, x_offset+200, y_offset+200, width=new_width * 0.5, height=new_height * 0.5)
        c.save()

    #Delete later
    def update_printbox(self):
        pass

    # Change between landscape/portrait previews
    def update_frame(self, selection):
        # Clear the current frame contents
        for widget in self.preview_label_frame.winfo_children():
            widget.destroy()

        page_size = 0

        if selection == "Landscape":
            self.preview_label_frame.configure(
                width=400, height=300
            )  # Set landscape dimensions
            self.text_box.configure(width=400)
            label = customtkinter.CTkLabel(
                self.preview_label_frame,
                text="Landscape Mode",
                font=("Arial", 16),
            )
            self.preview_label_frame.grid(
                row=2, column=0, sticky="nsew", padx=10, pady=10
            )
            
            page_size = landscape(A4)
            self.controller.set_page_size(page_size)
        elif selection == "Portrait":
            self.text_box.configure(width=200)
            self.preview_label_frame.configure(width=200, height=400)  # Set portrait dimensions
            label = customtkinter.CTkLabel(self.preview_label_frame, text="Portrait Mode", font=("Arial", 16))
            self.preview_label_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)

            page_size = A4
            self.controller.set_page_size(page_size)
        self.preview_label_frame.grid_propagate(False)
        self.create_preview_label(self.orientation_option_menu.get(),tab=self.controller.get_tab_info()[0])

    def create_preview_label(self, selection, tab=None, hazards=True):
        if selection == "Landscape":

            self.preview_label_frame.grid_columnconfigure(0, weight=1)
            
            #self.preview_topbar_frame = customtkinter.CTkFrame(self.preview_label_frame,corner_radius=0,height=40)
            #self.preview_topbar_frame.grid(row=0, column=0, padx=0, pady=0, sticky="nesw")
            
            #self.preview_topbar_frame.grid_propagate(False)

            self.preview_label_frame.grid_columnconfigure(0, weight=1)
            self.preview_label_frame.grid_columnconfigure(1, weight=1)
            self.preview_label_frame.grid_columnconfigure(2, weight=1)
            self.preview_label_frame.grid_columnconfigure(3, weight=0)

            #Logo
            self.logo_label_preview = customtkinter.CTkImage(dark_image=self.logo_image2, size=(160,40))
            self.logo_label = customtkinter.CTkLabel(
                self.preview_label_frame, 
                image=self.logo_label_preview, 
                text=""
                )  # Empty text for the image
            self.logo_label.grid(row=0, column=0, padx=10, sticky="w")

            #Barcode Preview Image
            self.barcode_image_prev = Image.open("barcode.png")
            self.barcode_photo_prev = customtkinter.CTkImage(dark_image=self.barcode_image_prev, size=(60,60))
            self.barcode_label_prev = customtkinter.CTkLabel(
                self.preview_label_frame,
                image=self.barcode_photo_prev,
                text=""
            )

            #Refresh barcode on tab switch
            self.generate_barcode(self.controller.get_new_barcode())
            self.barcode_photo_prev.configure(dark_image=Image.open(self.controller.get_barcode_image()))
            self.barcode_label_prev.configure(image=self.barcode_photo_prev)

            #QR Code Preview Image
            self.qr_code_image_preview = Image.open("resources\images\qr_code.png")
            self.qr_code_preview_photo = customtkinter.CTkImage(dark_image=self.qr_code_image_preview, size=(80,80))
            self.qr_code_label = customtkinter.CTkLabel(
                self.preview_label_frame, 
                image=self.qr_code_preview_photo, 
                text=""
            )

            self.preview_label_frame.grid_columnconfigure(0, weight=1)  # This will make the first column take up space
            self.preview_label_frame.grid_columnconfigure(1, weight=0)
            self.preview_label_frame.grid_columnconfigure(2, weight=1)
            
            self.barcode_label_prev.grid(row=0, column=1, padx=(0,15), sticky="w")
            self.qr_code_label.grid(row=0, column=2,padx=0,sticky="e")

            #Key Details
            #If labels exist already, delete them

            if self.preview_key_details.items():
                for widget in self.preview_key_details:
                    self.preview_key_details[widget].destroy()
                self.preview_key_details = {}
            
            max_rows_per_column = 4
            row = 1 
            for table in self.table_types:
                if str(tab).replace("_"," ") == table.lower():
                    table_columns_dict = self.controller.get_database_column_names(
                        self.table_types[''.join(table)]
                    )
                    for i, (key, column_list) in enumerate(table_columns_dict.items()):
                        
                        
                        # table_label_text = self.label_tables(key, i)
                        formatted_table_columns = self.format_names(column_list)

                        
                        #print(formatted_table_columns)
                        for j, column in enumerate(column_list):
                            # print(j," ",column)
                            if "id" in column.lower() or "hazard" in column.lower():
                                continue
                            elif "quantity" in column.lower():
                                words = column.lower().split("_")
                                formatted_table_columns[j] = words[0].title()
                            elif ("fk" in column.lower()):  # Change fk_location_general_inventory to 'Location'
                                words = column.lower().split("_")
                                words.remove("fk")
                                formatted_table_columns[j] = words[0].title()
                            
                            if key == "chemical_inventory":
                                selected_data = ['date', 'volume']
                                if column.lower() not in [x.lower() for x in selected_data]:
                                    continue
                                
                                
                            if key == "chemical_details":
                                selected_data = ['chemical_name', 'volume', 'concentration']
                                if column.lower() not in [x.lower() for x in selected_data]:
                                    continue
                            
                            if key == "general_product" and self.controller.get_tab_info()[0] != "general_inventory":
                                if "product" in column.lower():
                                    formatted_table_columns[j] = "Chemical Name"
                            
                            if self.controller.get_tab_info()[0] == "general_inventory":

                                selected_data = ['product_name', 'fk_location_general_inventory', 'product_description']
                                if column.lower() not in [x.lower() for x in selected_data]:
                                    continue

                                product = []
                                if "product_name" in column.lower():
                                    product.append(column.lower())
                                elif "location" in column.lower() and "product_name" in self.preview_key_details:
                                    product.append(column.lower())
                                elif "product_description" in column.lower() and "product_name" in self.preview_key_details and "location" in self.preview_key_details:
                                    product.append(column.lower())
                                
                                if product:
                                    label = customtkinter.CTkLabel(
                                        self.preview_label_frame, 
                                        text=formatted_table_columns[j] + ": ", 
                                        text_color="black",
                                        anchor="w",
                                        wraplength=250,
                                    )
                                    label.grid(row=row, column=0, padx=10, sticky="w")

                            
                            # Create the label for the row
                            label = customtkinter.CTkLabel(
                                self.preview_label_frame, 
                                text=formatted_table_columns[j] + ": ", 
                                text_color="black",
                                anchor="w",
                                wraplength=250,
                            )
                            label.grid(row=row, column=0, padx=10, sticky="w")
                            self.preview_key_details[column.lower()] = label

                            row += 1
                            if row >= max_rows_per_column:
                                break
            #     self.new_label_below = customtkinter.CTkLabel(
            #     self.preview_label_frame, 
            #     text="Chemical Name:",  # Multiline text
            #     text_color="black",
            #     anchor="w" 
            #     )
            #     self.new_label_below.grid(row=1, column=0, padx=10, sticky="w")
            # else:
            #     self.new_label_below = customtkinter.CTkLabel(
            #         self.preview_label_frame, 
            #         text="Concentration:",  # Multiline text
            #         text_color="black",
            #         anchor="w" 
            #     )
            #     self.new_label_below.grid(row=1, column=0, padx=10, sticky="w")

            #     self.new_label_below2 = customtkinter.CTkLabel(
            #         self.preview_label_frame, 
            #         text="Date Created:",  # Multiline text
            #         text_color="black",
            #         anchor="w" 
            #     )
            #     self.new_label_below2.grid(row=2, column=0, padx=10, sticky="w")
            self.preview_label_frame.grid_rowconfigure(1, weight=0)

            self.preview_label_frame.grid_columnconfigure(2, weight=1)  #Empty
            #Diamonds
            self.diamonds_preview_frame = customtkinter.CTkFrame(
                self.preview_label_frame, 
                width=120,
                height=120,
                fg_color = "transparent"
            )
            self.diamonds_preview_frame.place(x=270, y=160)
            self.diamonds_preview_frame.grid_propagate(False)

            self.diamonds_preview_frame.bind("<Configure>", self.on_diamond_frame_configure)

            # if self.controller.get_tab_info()[0] != "general_inventory":
            #     self.add_hazard_symbols(self.stored_diamonds)


            #Hazards/Precautions
            self.hazards_preview_textbox = customtkinter.CTkTextbox(
                self.preview_label_frame, 
                height=110,
                width=275,
                fg_color="transparent",
                text_color="black",
                wrap="word"
            )
            self.hazards_preview_textbox.grid(row=4, column=0, columnspan=1, padx=2,sticky="ew")

            if hazards or self.controller.get_tab_info()[0] != "general_inventory":
                self.hazards_preview_textbox.insert(tk.END,self.stored_preview_text)
            else:
                self.hazards_preview_textbox.delete("1.0", tk.END)
            
            self.address_label = customtkinter.CTkLabel(
                self.preview_label_frame, 
                text=self.default_address, 
                text_color="black",
                anchor="w",
                wraplength=300,
                fg_color="transparent"
            )
            self.address_label.grid(row=5, column=0, columnspan=1, padx=5,pady=(0,25),sticky="ew")
            self.preview_key_details["address"] = self.address_label
            

    def on_diamond_frame_configure(self,event):
        frame_height = self.diamonds_preview_frame.winfo_height()
    
        if frame_height > 1:
            if self.controller.get_tab_info()[0] != "general_inventory":
                if frame_height == 270:
                    self.diamonds_preview_frame.configure(width=180,height=180)
                    self.add_hazard_symbols(self.stored_diamonds)
            
            self.diamonds_preview_frame.unbind("<Configure>")
            
    def update_preview_box(self,args):
        text=args[0]
        hazard_symbols=args[1]
        self.hazards_preview_textbox.delete("1.0", tk.END)  # Clear the existing text
        self.hazards_preview_textbox.insert(tk.END, text)  # Insert the updated text
        self.stored_preview_text = text
        
        self.add_hazard_symbols(hazard_symbols)
                    
    
        # child_widgets = self.diamonds_preview_frame.winfo_children()
        # for widget in child_widgets:
        #     print(f"Widget: {widget} (Type: {widget.winfo_class()})")
        #self.diamonds_preview_frame.bind("<Configure>", self.update_image_size)
    
    def add_hazard_symbols(self,symbols=[]):
        self.remove_all_children(self.diamonds_preview_frame)
        
        #Exit function if no hazard symbols
        if not symbols: return
        
        min_width = 35  # Set a minimum width for the image
        num_hazard_labels = len(symbols)
       
        self.diamonds_preview_frame.configure(height=180)
        print(self.diamonds_preview_frame.winfo_height())
        label_width = max(int(180 * (1/num_hazard_labels)) - 5,min_width)
        label_height = max(int(180 * (1/num_hazard_labels)) - 5,min_width)
        
        row, col = 0, 0
        max_rows = 3
        max_cols = 3
        #Center diamond symbols
        if num_hazard_labels > 2:
            for r in range(max_rows):
                self.diamonds_preview_frame.grid_rowconfigure(r, weight=1, uniform="equal")  # Allows rows to stretch equally
            for c in range(max_cols):
                self.diamonds_preview_frame.grid_columnconfigure(c, weight=1, uniform="equal")  # Allows columns to stretch equally
        else:
            for r in range(max_rows):
                self.diamonds_preview_frame.grid_rowconfigure(r, weight=0, uniform="equal")  # Allows rows to stretch equally
            for c in range(max_cols):
                self.diamonds_preview_frame.grid_columnconfigure(c, weight=0, uniform="equal")  # Allows columns to stretch equally
        diamonds_dict = self.controller.get_hazard_diamonds_dict()['Diamonds']
        for item in diamonds_dict:
            for i,symbol in enumerate(symbols):
                #print(f"Does {item[0]} | equal | {symbol}?")
                if item[0] == symbol:
                    image = Image.open(item[1])
                    resized_image = image.resize((label_width, label_height), Image.LANCZOS)
                    image = ImageTk.PhotoImage(resized_image)
                    hazard_label = customtkinter.CTkLabel(self.diamonds_preview_frame, image=image, text="")
                    hazard_label.grid(row=row, column=col, sticky="nsew")

                    col += 1

                    # If the column reaches the max number of columns, reset it to 0 and move to the next row
                    if col >= max_cols:
                        col = 0
                        row += 1

            # If the number of rows reaches the max, break out of the loop
            if row >= max_rows:
                break
        
        self.stored_diamonds = symbols
    
    def switch_preview_box(self):
        #Clear entries from current tab
        self.controller.clear_data_entries()
        self.create_preview_label(self.orientation_option_menu.get(),self.controller.get_tab_info()[0],hazards=False)

    def remove_all_children(self,frame):
        for widget in frame.winfo_children():
            widget.destroy()

class HazardPrecautionFrame(customtkinter.CTkFrame):
    def __init__(self, parent, controller, warning_dict, root, images=False):
        super().__init__(parent)
        self.parent = parent
        self.root = root
        first_key = list(warning_dict.keys())[0]
        self.controller = controller

        # Signal Word selection
        self.warning_type_var = customtkinter.StringVar(
            value=first_key
        )  # Default value

        # Hazard dropdown menu
        self.warning_type_menu = customtkinter.CTkComboBox(
            self,
            variable=self.warning_type_var,
            values=list(warning_dict.keys()),
            command=self.on_dropdown_change,
        )
        self.warning_type_menu.grid(
            row=0, column=1, padx=10, pady=5, sticky="ew"
        )
        self.grid_columnconfigure(1, weight=3)

        # Exit dropdowns
        self.close_button = customtkinter.CTkButton(
            self, text="Close", fg_color="gray",command=self.close_checkboxes
        )
        self.close_button.grid(row=0, column=2, padx=5, pady=5, sticky="ne")

        self.warning_type = None

        if "hazard" in first_key.lower():
            self.warning_type = "Hazard"
        elif "precautionary" in first_key.lower():
            self.warning_type = "Precaution"
        elif "diamond" in first_key.lower():
            self.warning_type = "Diamond"

        self.select_warning_label = customtkinter.CTkLabel(
            self, text=f"Select {self.warning_type} Type:"
        )
        self.select_warning_label.grid(row=0, column=0, padx=10, pady=5)

        self.warning_type_frames = {}
        for i, warning_type in enumerate(list(warning_dict.keys())):
            if i == 0:
                frame = WarningClassCheckboxes(
                    self,
                    warning_dict[warning_type],
                    default_class=True,
                    images=images,
                )
                # frame.grid(row=1, column=0,padx=10, pady=5)
            else:
                frame = WarningClassCheckboxes(
                    self,
                    warning_dict[warning_type],
                    images=images,
                )
                # frame.grid(row=1, column=0, padx=10, pady=5)
                self.hide_frames()
            self.warning_type_frames[warning_type] = frame
        self.warning_type_var.trace("w", self.switch_frame)

    def switch_frame(self, *args):
        the_frame = self.warning_type_var.get()
        if not the_frame:
            # print("frame is empty.")
            pass
        else:
            self.hide_frames()
            self.show_frame(self.warning_type_frames[the_frame])
            # print(f"Switched to {the_frame} frame")

    def show_frame(self, frame):
        frame.grid(row=1, column=0, columnspan=5, padx=10, pady=5, sticky="ew")

    def hide_frames(self):
        for frame in self.warning_type_frames.values():
            frame.grid_forget()

    def on_dropdown_change(self, value):
        self.warning_type_frames[value].show_checkboxes()

    def close_checkboxes(self, event=None):
        the_frame = self.warning_type_var.get()
        self.warning_type_frames[the_frame].grid_forget()

    # Future Idea - Maybe remove textbox clearing when switching warning_type
    def update_text_box(self):
        text = ""
        selections = self.controller.get_haz_prec_diamonds()
        
        # if self.warning_type == "Hazard":
        #     warning_vars = self.controller.get_selected_hazards()
        # elif self.warning_type == "Precaution":
        #     warning_vars = self.controller.get_selected_precautions()
        # elif self.warning_type == "Diamond":
        #     warning_vars = self.controller.get_diamond_vars()

        # if warning_vars is not None:
        #     for var, label, *rest in warning_vars:
        #         if var.get():
        #             text += f"{label}\n"
        #     self.root.text_box.delete("1.0", tk.END)  # Clear the existing text
        # self.root.text_box.insert(tk.END, text)  # Insert the updated text

        #Change hazard text box
        if selections is not None:
            for var, label, *rest in selections:
                if var.get():
                    text += f"{label}\n"
            self.root.text_box.delete("1.0", tk.END)  # Clear the existing text
        self.root.text_box.insert(tk.END, text)  # Insert the updated text

        #Change diamonds
        diamonds = self.controller.get_diamond_vars()
        diamond_images = []
        if diamonds is not None:
            for var, label, *rest in diamonds:
                if var.get():
                    diamond_images.append(label)
        
        #Finally, update preview box
        self.root.update_preview_box([text,diamond_images])


class WarningClassCheckboxes(customtkinter.CTkScrollableFrame):
    def __init__(
        self, parent, warning_items, default_class=False, images=False
    ):
        super().__init__(parent)
        self.parent = parent
        self.warning_items = warning_items

        if self.parent.warning_type == "Diamond":
            self.generate_diamonds(images=images)
        else:
            self.generate_checkboxes(images=images)

        if default_class:
            self.grid(
                row=1, column=0, columnspan=5, padx=10, pady=5, sticky="ew"
            )

        self.checkboxes_frame = customtkinter.CTkFrame(self)
        # Issue - checkboxes_frame covers up text for dropdown checkboxes
        # self.checkboxes_frame.grid(row=0, column=0)

    def generate_diamonds(self, images=False):
        for item in self.warning_items:
            if images:
                image = Image.open(item[1])
                resized_image = image.resize((100, 100), Image.LANCZOS)
                image = ImageTk.PhotoImage(
                    resized_image
                )  # Convert to a PhotoImage object
                item_text = item[0]
            else:
                image = None
                item_text = item[0]

            var = tk.BooleanVar()

            item_frame = customtkinter.CTkFrame(self)
            item_frame.pack(anchor="w", pady=5)

            checkbox = customtkinter.CTkCheckBox(
                item_frame,
                text=None,
                variable=var,
                width=0,
                command=lambda var=var: self.parent.update_text_box(),
            )
            checkbox.pack(side="left", fill="x", padx=5)

            image_label = customtkinter.CTkLabel(
                item_frame, text=None, image=image
            )
            image_label.image = image  # Keep reference to image
            image_label.pack(
                side="left", padx=5
            )  # Pack the image label next to the checkbox

            diamond_label = customtkinter.CTkLabel(item_frame, text=item_text)
            diamond_label.pack(side="left", padx=5)

            # Keep track of checkbox vars and labels
            if self.parent.warning_type == "Hazard":
                self.parent.controller.append_hazard_variables(var, item)
            elif self.parent.warning_type == "Precaution":
                self.parent.controller.append_precautions_variables(var, item)
            elif self.parent.warning_type == "Diamond":
                self.parent.controller.append_diamond_variables(
                    var, item[0], image
                )

    def generate_checkboxes(self, images=False):
        self.checkbox_frame = customtkinter.CTkFrame(self)
        # self.checkbox_frame.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.checkbox_frame.grid_forget()

        self.checkboxes = []

        for widget in self.checkboxes:
            widget.grid_forget()
        self.checkboxes.clear()

        for idx, item in enumerate(self.warning_items):

            var = tk.BooleanVar()

            checkbox = customtkinter.CTkCheckBox(
                self,
                text=item,
                variable=var,
                onvalue=True,
                offvalue=False,
                command=lambda var=var: self.parent.update_text_box(),
            )
            checkbox.grid(row=idx, column=0, padx=10, pady=5, sticky="ew")
            self.checkboxes.append(checkbox)

            # Keep track of checkbox vars and labels
            if self.parent.warning_type == "Hazard":
                self.parent.controller.append_hazard_variables(var, item)
            elif self.parent.warning_type == "Precaution":
                self.parent.controller.append_precautions_variables(var, item)

    def show_checkboxes(self, event=None):
        pass


# if __name__ == "__main__":
# app = App()
# app.mainloop()
