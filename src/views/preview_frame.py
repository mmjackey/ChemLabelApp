import tkinter as tk

import customtkinter
from PIL import Image
from reportlab.lib.pagesizes import A4, landscape

from config import AppConfig


class PreviewFrame(customtkinter.CTkFrame):
    def __init__(self, parent, controller, root):
        super().__init__(parent)

        self.controller = controller
        self.parent = parent
        self.root = root

        # Configure columns
        for col in range(4):  # Configure columns 0 to 3 with weight=1
            self.grid_columnconfigure(col, weight=1)

        # Orientation Selection - Landscape or Portrait
        self.area_4_header = customtkinter.CTkLabel(
            self,
            text="Preview",
            font=customtkinter.CTkFont(size=18, weight="bold"),
        )
        self.area_4_header.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.orientation_option_menu = customtkinter.CTkOptionMenu(
            self,
            values=["Landscape", "Portrait"],
            command=self.update_frame,
        )
        self.orientation_option_menu.grid(
            row=1, column=0, sticky="nsew", padx=10, pady=10
        )

        # Preview Label frame
        self.preview_label_frame = customtkinter.CTkFrame(
            self, fg_color="#FAF9F6", corner_radius=0
        )
        self.preview_label_frame.grid(
            row=2, column=0, sticky="nsew", padx=10, pady=10
        )

        # Set initial landscape preview
        self.update_frame(self.orientation_option_menu.get())

    def update_frame(self, selection):
        # Clear the current frame contents
        for widget in self.preview_label_frame.winfo_children():
            widget.destroy()

        page_size = 0

        if selection == "Landscape":
            self.preview_label_frame.configure(
                width=420, height=300
            )  # Set landscape dimensions
            self.root.area_5.text_box.configure(width=400)
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
            self.root.area_5.text_box.configure(width=200)
            self.preview_label_frame.configure(
                width=200, height=400
            )  # Set portrait dimensions
            label = customtkinter.CTkLabel(
                self.preview_label_frame,
                text="Portrait Mode",
                font=("Arial", 16),
            )
            self.preview_label_frame.grid(
                row=2, column=0, sticky="nsew", padx=10, pady=10
            )

            page_size = A4
            self.controller.set_page_size(page_size)
        self.preview_label_frame.grid_propagate(False)
        self.create_preview_label(
            self.orientation_option_menu.get(),
            tab=self.controller.get_tab_info()[0],
        )

    def create_preview_label(self, selection, tab=None, hazards=True):
        if selection == "Landscape":
            # Configure grid columns
            for col in range(4):
                weight = 1 if col < 3 else 0
                self.preview_label_frame.grid_columnconfigure(
                    col, weight=weight
                )

            # Logo Label
            self.logo_label = self.create_image_label(
                AppConfig.LOGO_PREVIEW,
                (160, 40),
                row=0,
                column=0,
                padx=10,
                sticky="w",
            )

            # Barcode Preview Label
            self.barcode_photo_prev = customtkinter.CTkImage(
                dark_image=Image.open(AppConfig.BARCODE), size=(60, 60)
            )
            self.barcode_label_prev = self.create_image_label(
                "barcode.png",
                (60, 60),
                row=0,
                column=1,
                padx=(0, 15),
                sticky="w",
            )
            self.barcode_label_prev.configure(image=self.barcode_photo_prev)

            # QR Code Preview Label
            self.qr_code_label = self.create_image_label(
                "resources/images/qr_code.png",
                (80, 80),
                row=0,
                column=2,
                sticky="e",
            )

            # Reset key details if they exist
            self.clear_preview_key_details()

            # Create and filter table columns based on tab selection
            row = 1
            max_rows_per_column = 4

            for table in self.root.table_types:
                if "batch" in tab:
                    tab = "product_inventory"
                # print(f"Does {tab.replace("_", " ").lower()} in {table.lower()}?")
                if str(tab).replace("_", " ").lower() in table.lower():
                    self.create_table_columns(table, row, max_rows_per_column)
                    if row >= max_rows_per_column:
                        break

            # Diamonds preview frame
            self.create_diamonds_frame()

            # Hazards/Precautions Textbox
            self.hazards_preview_textbox = customtkinter.CTkTextbox(
                self.preview_label_frame,
                height=110,
                width=275,
                fg_color="transparent",
                text_color="black",
                wrap="word",
            )
            self.hazards_preview_textbox.grid(
                row=4, column=0, columnspan=1, padx=2, sticky="ew"
            )
            if (
                hazards
                or self.controller.get_tab_info()[0] != "general_inventory"
            ):
                self.hazards_preview_textbox.insert(
                    tk.END, self.root.stored_preview_text
                )
            else:
                self.hazards_preview_textbox.delete("1.0", tk.END)

            # Address label
            self.address_label = customtkinter.CTkLabel(
                self.preview_label_frame,
                text=self.root.default_address,
                text_color="black",
                anchor="w",
                wraplength=300,
                fg_color="transparent",
            )
            self.address_label.grid(
                row=5,
                column=0,
                columnspan=1,
                padx=5,
                pady=(0, 25),
                sticky="ew",
            )
            self.root.preview_key_details["address"] = self.address_label

        self.preview_label_frame.grid_rowconfigure(1, weight=0)
        self.preview_label_frame.grid_columnconfigure(
            2, weight=1
        )  # Empty column for spacing

        if self.controller.get_tab_info()[0] != "general_inventory":
            self.add_hazard_symbols(self.root.stored_diamonds)

    def create_image_label(
        self, image_path, size, row, column, sticky, padx=(0, 0)
    ):
        """Helper function to create image labels with custom size."""
        image = Image.open(image_path)
        image_preview = customtkinter.CTkImage(dark_image=image, size=size)
        label = customtkinter.CTkLabel(
            self.preview_label_frame, image=image_preview, text=""
        )
        label.grid(row=row, column=column, padx=padx, sticky=sticky)
        return label

    def clear_preview_key_details(self):
        """Clear any existing preview key details."""
        if self.root.preview_key_details.items():
            for widget in self.root.preview_key_details.values():
                widget.destroy()
            self.root.preview_key_details = {}

    def create_table_columns(self, table, row, max_rows_per_column):
        """Helper function to create and filter table columns based on selection."""
        table_columns_dict = self.controller.get_database_column_names(
            self.root.table_types["".join(table)]
        )
        for i, (key, column_list) in enumerate(table_columns_dict.items()):
            formatted_table_columns = self.root.format_names(column_list)

            for j, column in enumerate(column_list):
                if self.should_skip_column(key, column):
                    continue

                label = customtkinter.CTkLabel(
                    self.preview_label_frame,
                    text=f"{formatted_table_columns[j]}: ",
                    text_color="black",
                    anchor="w",
                    wraplength=250,
                )
                label.grid(row=row, column=0, padx=10, sticky="w")
                self.root.preview_key_details[column.lower()] = label
                row += 1
                if row >= max_rows_per_column:
                    break

    def should_skip_column(self, key, column):
        """Helper function to determine whether to skip a column based on conditions."""
        column_lower = column.lower()
        if "id" in column_lower or "hazard" in column_lower:
            return True
        if "quantity" in column_lower:
            return True
        if "fk" in column_lower:
            return True
        if key == "chemical_inventory" and column_lower not in [
            "date",
            "volume",
        ]:
            return True
        if key == "chemical_details" and column_lower not in [
            "chemical_name",
            "volume",
            "concentration",
        ]:
            return True
        if (
            key == "general_product"
            and self.controller.get_tab_info()[0] != "general_inventory"
            and "product" in column_lower
        ):
            return True
        if key == "general_inventory" and column_lower not in [
            "product_name",
            "fk_location_general_inventory",
            "product_description",
        ]:
            return True
        return False

    def create_diamonds_frame(self):
        """Create and configure the diamonds preview frame."""
        self.diamonds_preview_frame = customtkinter.CTkFrame(
            self.preview_label_frame,
            width=120,
            height=120,
            fg_color="transparent",
        )
        self.diamonds_preview_frame.place(x=290, y=160)
        self.diamonds_preview_frame.grid_propagate(False)
        self.diamonds_preview_frame.bind(
            "<Configure>", self.on_diamond_frame_configure
        )

    def on_diamond_frame_configure(self, event):
        frame_height = self.diamonds_preview_frame.winfo_height()

        if frame_height > 1:
            if self.controller.get_tab_info()[0] != "general_inventory":
                if frame_height == 270:
                    self.diamonds_preview_frame.configure(
                        width=120, height=120
                    )
                    self.root.add_hazard_symbols(self.root.stored_diamonds)

            self.diamonds_preview_frame.unbind("<Configure>")

    def add_hazard_symbols(self, symbols=[]):
        self.remove_all_children(self.diamonds_preview_frame)

        # Exit function if no hazard symbols
        if not symbols:
            return

        min_width = 35  # Set a minimum width for the image
        num_hazard_labels = len(symbols)

        self.diamonds_preview_frame.configure(height=120)
        # print(self.diamonds_preview_frame.winfo_height())
        label_width = max(int(180 * (1 / num_hazard_labels)) - 5, min_width)
        label_height = max(int(180 * (1 / num_hazard_labels)) - 5, min_width)

        row, col = 0, 0
        max_rows = 3
        max_cols = 3
        # Center diamond symbols
        if num_hazard_labels > 2:
            for r in range(max_rows):
                self.diamonds_preview_frame.grid_rowconfigure(
                    r, weight=1, uniform="equal"
                )  # Allows rows to stretch equally
            for c in range(max_cols):
                self.diamonds_preview_frame.grid_columnconfigure(
                    c, weight=1, uniform="equal"
                )  # Allows columns to stretch equally
        else:
            for r in range(max_rows):
                self.diamonds_preview_frame.grid_rowconfigure(
                    r, weight=0, uniform="equal"
                )  # Allows rows to stretch equally
            for c in range(max_cols):
                self.diamonds_preview_frame.grid_columnconfigure(
                    c, weight=0, uniform="equal"
                )  # Allows columns to stretch equally
        diamonds_dict = self.controller.get_hazard_diamonds_dict()["Diamonds"]
        for item in diamonds_dict:
            for i, symbol in enumerate(symbols):
                # print(f"Does {item[0]} | equal | {symbol}?")
                if item[0] == symbol:
                    image = Image.open(item[1])
                    resized_image = image.resize(
                        (label_width, label_height), Image.LANCZOS
                    )

                    ctk_image = customtkinter.CTkImage(
                        light_image=resized_image, dark_image=resized_image
                    )

                    hazard_label = customtkinter.CTkLabel(
                        self.diamonds_preview_frame, image=ctk_image, text=""
                    )
                    hazard_label.grid(row=row, column=col, sticky="nsew")

                    col += 1

                    # If the column reaches the max number of columns, reset it to 0 and move to the next row
                    if col >= max_cols:
                        col = 0
                        row += 1

            if row >= max_rows:
                break

        self.root.stored_diamonds = symbols

    def remove_all_children(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()

    def switch_preview_box(self):
        # Clear entries from current tab
        self.controller.clear_data_entries()
        self.create_preview_label(
            self.orientation_option_menu.get(),
            self.controller.get_tab_info()[0],
            hazards=False,
        )
