import math
import tkinter as tk
from tkinter import Tk, filedialog, messagebox, ttk

import customtkinter
from PIL import Image, ImageTk

from config import AppConfig

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

        #See if table exists
        #print(self.product_keys)

        
        # Load warning dictionaries
        hazard_warnings = self.controller.get_hazard_classes_dict()
        precaution_warnings = self.controller.get_precaution_classes_dict()
        hazard_diamonds = self.controller.get_hazard_diamonds_dict()

        self.item_type_frames = {}
        self.tab_buttons = []

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
        self.logo_image = Image.open("C:/Users/Blake/Documents/ChemLabelApp/resources/images/sofab_logo.png")
        self.logo_image2 = Image.open("resources\images\sofab_logo2.png")
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
        
        # Create initial window
        self.geometry("1200x768")
        self.window_frame = customtkinter.CTkScrollableFrame(
            self, fg_color="transparent"
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
        self.create_area_1(self.chem_inventory_keys)

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
        self.area_1 = customtkinter.CTkFrame(self.window_frame, corner_radius=10)
        self.area_1.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

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
            #print(formatted_table_columns)
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
        self.preview_label_frame = customtkinter.CTkFrame(self.area_4,fg_color="white")
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
        if button_name.lower() == ''.join(self.chem_inventory_keys).lower():
            self.area_2.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
            self.area_3.grid(row=3, column=0, sticky="nsew", padx=10, pady=10)
            self.area_5.grid(
            row=2, column=1, columnspan=2, sticky="nsew", padx=10, pady=10
            )
            self.create_area_1(self.chem_inventory_keys)
        if button_name.lower() == ''.join(self.gen_inventory_keys).lower():
            self.area_2.grid_forget()
            self.area_3.grid_forget()
            self.area_5.grid_forget()
            self.create_area_1(self.gen_inventory_keys)
        if button_name.lower() == ''.join(self.chem_details).lower():
            self.area_2.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
            self.area_3.grid(row=3, column=0, sticky="nsew", padx=10, pady=10)
            self.area_5.grid(
            row=2, column=1, columnspan=2, sticky="nsew", padx=10, pady=10
            )
            self.create_area_1(self.chem_details)

        #Refresh preview label
        self.switch_preview_box()
    
    def update_key_details(self, *args):
        
        #Load StringVar object
        entry_name = args[0]
        str_var = self.entry_strings[args[1]]
        
        
        #self.area_1_entries[entry_name] = str_var.get()
        self.controller.set_data_entries(entry_name,str_var.get())
        
        # Do something with the updated value (for now, just print it)
        #print(f"Entry {args[0]} updated: {str_var.get()}")
        print(self.controller.get_data_entries())

    #Not quite there yet
    def on_submit(self):
        print("Print to PDF")
        for entry_field in self.entry_vars.keys():
            #print(f"{entry_field}: {self.entry_vars[entry_field].get()}")
            entry = self.entry_vars[entry_field].get()
    
    #Delete later
    def update_printbox(self):
        pass

    # Change between landscape/portrait previews
    def update_frame(self, selection):
        # Clear the current frame contents
        for widget in self.preview_label_frame.winfo_children():
            widget.destroy()

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
        elif selection == "Portrait":
            self.text_box.configure(width=200)
            self.preview_label_frame.configure(width=200, height=400)  # Set portrait dimensions
            label = customtkinter.CTkLabel(self.preview_label_frame, text="Portrait Mode", font=("Arial", 16))
            self.preview_label_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
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

            self.logo_label_preview = customtkinter.CTkImage(dark_image=self.logo_image2, size=(160,40))
            self.logo_label = customtkinter.CTkLabel(
                self.preview_label_frame, 
                image=self.logo_label_preview, 
                text=""
                )  # Empty text for the image
            self.logo_label.grid(row=0, column=0, padx=10, sticky="w")

            #Barcode Preview Image
            self.barcode_image_prev = Image.open("barcode.png")
            self.barcode_photo_prev = customtkinter.CTkImage(dark_image=self.barcode_image_prev, size=(80,80))
            self.barcode_label_prev = customtkinter.CTkLabel(
                self.preview_label_frame,
                image=self.barcode_photo_prev,
                text=""
            )

            #QR Code Preview Image
            self.qr_code_image_preview = Image.open("C:/Users/Blake/Documents/ChemLabelApp/resources/images/qr_code.png")
            self.qr_code_preview_photo = customtkinter.CTkImage(dark_image=self.qr_code_image_preview, size=(80,80))
            self.qr_code_label = customtkinter.CTkLabel(
                self.preview_label_frame, 
                image=self.qr_code_preview_photo, 
                text=""
            )

            self.preview_label_frame.grid_columnconfigure(0, weight=1)  # This will make the first column take up space
            self.preview_label_frame.grid_columnconfigure(1, weight=0)
            self.preview_label_frame.grid_columnconfigure(2, weight=0)
            
            self.barcode_label_prev.grid(row=0, column=1, padx=5, pady=5, sticky="w")
            self.qr_code_label.grid(row=0, column=2,padx=5, sticky="e")

            #Key Details
            max_rows_per_column = 3
            row = 1 
            for table in self.table_types:
                if str(tab).replace("_"," ") == table.lower():
                    table_columns_dict = self.controller.get_database_column_names(
                        self.table_types[''.join(table)]
                    )
                    for i, (key, column_list) in enumerate(table_columns_dict.items()):
                        
                        
                        # table_label_text = self.label_tables(key, i)
                        formatted_table_columns = self.format_names(column_list)

                        if key == "chemical_details":
                            print(formatted_table_columns)
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

                            # Create the label for the row
                            label = customtkinter.CTkLabel(
                                self.preview_label_frame, 
                                text=formatted_table_columns[j] + ": ", 
                                text_color="black",
                                anchor="w",
                            )
                            label.grid(row=row, column=0, padx=10, sticky="ew")
                        
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

            #Hazards/Precautions
            self.hazards_preview_textbox = customtkinter.CTkTextbox(
                self.preview_label_frame, 
                height=150,
                fg_color="transparent",
                text_color="black",
            )
            self.hazards_preview_textbox.grid(row=4, column=0, columnspan=3, padx=2,sticky="ew")

            if hazards or self.controller.get_tab_info()[0] != "general_inventory":
                self.hazards_preview_textbox.insert(tk.END,self.stored_preview_text)
            else:
                self.hazards_preview_textbox.delete("1.0", tk.END)
            self.preview_label_frame.grid_columnconfigure(2, weight=1)  #Empty

            #Diamonds
            # diamonds = self.controller.get_diamond_vars()
            # if diamonds is not None:
            #     for var, label, *rest in diamonds:
            #         if var.get():
            #             #print(var.get())
            

            self.diamonds_preview_frame = customtkinter.CTkFrame(
                self.preview_label_frame, 
                width=120,
                height=120,
                fg_color = "transparent"
            )
            self.diamonds_preview_frame.place(x=260, y=160)
            self.diamonds_preview_frame.grid_propagate(False)

            if self.controller.get_tab_info()[0] != "general_inventory":
                self.add_hazard_symbols(self.stored_diamonds)


            
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

        #Exit function if no hazard symbols
        if not symbols: return

        self.remove_all_children(self.diamonds_preview_frame)
        min_width = 55  # Set a minimum width for the image
        num_hazard_labels = len(symbols)
        label_width = max(int(175 * (1/num_hazard_labels)) - 5,min_width)
        label_height = max(int(175 * (1/num_hazard_labels)) - 5,min_width)
        
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
