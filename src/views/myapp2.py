import tkinter as tk
from tkinter import messagebox

import customtkinter
import qrcode
from barcode import Code128
from barcode.writer import ImageWriter
from CTkMessagebox import CTkMessagebox
from PIL import Image, ImageGrab
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas

from config import AppConfig
from views.details_selection_frame import DetailSelectFrame
from views.preview_frame import PreviewFrame
from views.warning_print_frame import WarningPrintFrame
from views.warning_select_frame import HazardSymbolFrame, WarningSelectFrame


class MyApp2(customtkinter.CTk):
    def __init__(self, controller):
        super().__init__()

        self.controller = controller
        self.controller.set_view(self)

        self.title("SoFab Inks Inventory Management")

        item_type_tables = self.controller.get_item_type_tables()
        self.table_types = item_type_tables

        # Sensitive - Move somewhere else
        self.default_address = "11351 Decimal Drive Louisville, KY 40299"

        self.current_tab = None

        self.tab_buttons = []
        self.preview_key_details = {}

        self.area_1_frames = []

        # Get latest id from chosen inventory type
        default = list(self.table_types)[0]
        self.inventory_type = default
        self.controller.set_id_info(
            self.inventory_type.replace(" ", "_"),
            self.controller.next_id(
                self.controller.database.get_latest_barcode_id(
                    self.inventory_type
                )
            ),
        )
        self.controller.set_new_barcode(
            self.controller.get_id_info()[
                self.inventory_type.replace(" ", "_")
            ]
        )

        # Topbar - Chemical/General/Details Inventory and Submit
        self.setup_menu()

        # Dark mode
        customtkinter.set_appearance_mode("dark")

        # Configure window grid columns
        self.configure_window_grid()

        # Create initial window and frame
        self.geometry("1400x840")

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

        # Topbar - SoFab Logo!
        self.logo_photo = customtkinter.CTkImage(
            dark_image=Image.open(AppConfig.SOFAB_LOGO), size=(160, 40)
        )
        self.logo_label = customtkinter.CTkLabel(
            self.topbar_frame, image=self.logo_photo, text=""
        )  # Empty text for the image
        self.logo_label.grid(row=0, column=0, padx=10, pady=10)

        # Topbar - Menu buttons
        last_column = self.initialize_tab_buttons(self.table_types)

        # Topbar - Submit
        self.submit_button = customtkinter.CTkButton(
            self.topbar_frame,
            text="Submit",
            command=lambda: self.on_submit(),
            fg_color="transparent",
            border_width=0,
        )
        self.submit_button.grid(
            row=0, column=last_column + 1, padx=10, pady=10
        )

    # Chemical Inventory, General Inventory, Batch Inventory, Submit
    def initialize_tab_buttons(self, table):
        tab_column_index = 1
        for i, key in enumerate(table):
            topbar_button = customtkinter.CTkButton(
                self.topbar_frame,
                text=key,
                command=lambda name=key: self.sidebar_button_event(name),
                fg_color="transparent",
                border_width=0,
            )
            topbar_button.grid(
                row=0, column=1 + tab_column_index, padx=10, pady=10
            )
            self.tab_buttons.append(topbar_button)
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
        self.area_5 = WarningPrintFrame(self, self.controller)
        self.area_5.grid(
            row=2, column=1, columnspan=2, sticky="nsew", padx=10, pady=10
        )
        table = list(self.table_types)[0]
        # Key Chemical Details
        self.area_1 = DetailSelectFrame(
            self,
            self.controller,
            table,
        )
        self.area_1.configure(corner_radius=10)
        self.area_1.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        # Contains hazards and precautions
        self.area_2 = WarningSelectFrame(
            self,
            self.controller,
            hazard_warnings,
            precaution_warnings,
            root=self,
        )
        self.area_2.configure(corner_radius=10)
        self.area_2.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)

        # Create hazard symbols frame
        self.area_3 = HazardSymbolFrame(
            self,
            self.controller,
            hazard_diamonds,
            hazard_print=self.area_5.text_box,
            root=self,
        )
        self.area_3.configure(corner_radius=10)
        self.area_3.grid(row=3, column=0, sticky="nsew", padx=10, pady=10)

        # Contains Preview box and orientation selection
        self.area_4 = PreviewFrame(self, self.controller, root=self)
        self.area_4.configure(corner_radius=10)
        self.area_4.grid(
            row=1, column=1, columnspan=2, sticky="nsew", padx=10, pady=10
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

    def format_names(self, names):
        """Ex: chemical_inventory -> Chemical Inventory"""
        if type(names) is list:
            return [name.replace("_", " ").title() for name in names]
        elif type(names) is str:
            return names.replace("_", " ").title()

    def sidebar_button_event(self, button_name):
        """Switch between Inventory Types"""
        value = button_name.title()
        self.current_tab = value
        self.inventory_type = value.lower()
        self.update_area_layout(
            value
        )  # Update layout for selected inventory type
        self.create_area_frame(value)  # Create the corresponding area frame

        # Refresh preview label
        self.area_4.switch_preview_box()

    def update_area_layout(self, area_to_show):
        # Reset all areas
        self.area_2.grid_forget()
        self.area_3.grid_forget()
        self.area_5.grid_forget()

        # Apply layout for the selected area
        if area_to_show == "Chemical Inventory":
            self.area_2.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
            self.area_3.grid(row=3, column=0, sticky="nsew", padx=10, pady=10)
            self.area_5.grid(
                row=2, column=1, columnspan=2, sticky="nsew", padx=10, pady=10
            )

    def create_area_frame(self, inventory_type):
        # take inventory type and find the key in 'area_mappings' that corresponds to it.
        value = inventory_type.title()
        # keep ref to old frame
        self.area_1_frames.append(self.area_1)

        self.area_1 = DetailSelectFrame(self, self.controller, value)

        self.area_1.configure(corner_radius=10)
        self.area_1.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

    # When add to database is toggled
    def checkbox_changed(self):
        if self.area_1.add_to_db_var.get() == "on":
            self.controller.set_db_insertion(True, self.current_tab)
        else:
            self.controller.set_db_insertion(False, self.current_tab)

    # Not quite there yet
    def on_submit(self):
        tab_dict = self.controller.retrieve_tab_entries(self.current_tab)
        table = list(tab_dict.keys())[0]

        self.controller.on_submission2(table, self.current_tab)

        # Create new barcode
        self.generate_barcode(self.controller.get_new_barcode())
        self.area_4.barcode_photo_prev.configure(
            dark_image=Image.open(self.controller.get_barcode_image())
        )
        self.area_4.barcode_label_prev.configure(
            image=self.area_4.barcode_photo_prev
        )

        # Create new qr_code
        self.generate_qr_code(self.controller.get_qr_code_entry())
        new_qr_code = customtkinter.CTkImage(
            dark_image=Image.open(self.controller.get_qr_code_image()),
            size=(80, 80),
        )
        self.area_4.qr_code_label.configure(image=new_qr_code)

        # image_width = self.qr_code_image_preview.size[0]
        self.area_4.barcode_label_prev.grid(
            row=0, column=1, padx=0, sticky="w"
        )
        self.area_4.qr_code_label.grid(
            row=0, column=2, padx=(0, 5), sticky="e"
        )
        # self.qr_code_label.grid(padx=(0,15))

        self.capture_widget_as_image(self.area_4.preview_label_frame)
        self.create_pdf(
            "widget_capture.png",
        )

        # Refresh Entry boxes
        # for box in self.area_1.entry_vars.values():
        #    box.delete(0, tk.END)

        print("PDF created successfully!")
        self.controller.set_id_info(
            self.inventory_type.replace(" ", "_"),
            self.controller.next_id(
                self.controller.database.get_latest_barcode_id(
                    self.inventory_type
                )
            ),
        )
        self.controller.set_new_barcode(
            self.controller.get_id_info()[
                self.inventory_type.replace(" ", "_")
            ]
        )
        self.generate_barcode(self.controller.get_new_barcode())
        self.area_4.update_frame("Landscape")

    def generate_barcode(self, input_string):
        try:
            file_name = "barcode"
            my_code = Code128(input_string, writer=ImageWriter())
            my_code.save(file_name)  # Save the barcode as "barcode.png"
            self.controller.set_barcode_image(f"{file_name}.png")
            return f"{file_name}.png"  # Return the file path for later use
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return None

    def generate_qr_code(self, input_string):
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

    def capture_widget_as_image(self, widget, filename="widget_capture.png"):
        # Get the widget's bounding box
        x = widget.winfo_rootx()
        y = widget.winfo_rooty()
        width = widget.winfo_width()
        height = widget.winfo_height()

        img = ImageGrab.grab(bbox=(x, y, (x + width), (y + height)))
        new_image = img.rotate(-90)
        new_image = img.convert("RGB")

        new_image.save(filename)

    def create_pdf(self, image_path, pdf_filename="output.pdf"):
        img = Image.open(image_path)
        if img.mode == "RGBA":
            img = img.convert("RGB")
        img.save(pdf_filename)

    # Delete later
    def update_printbox(self):
        pass

    def update_preview_box(self, args):
        text = args[0]
        hazard_symbols = args[1]
        self.area_4.hazards_preview_textbox.delete(
            "1.0", tk.END
        )  # Clear the existing text
        self.area_4.hazards_preview_textbox.insert(
            tk.END, text
        )  # Insert the updated text
        self.stored_preview_text = text

        self.area_4.add_hazard_symbols(hazard_symbols)

    def data_error_message(self, err):
        CTkMessagebox(title="Error", message=err, icon="cancel")
        self.area_1.add_to_db_var.set(value="off")
