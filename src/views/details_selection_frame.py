import customtkinter


class DetailSelectFrame(customtkinter.CTkFrame):
    def __init__(self, parent, controller, table, root):
        super().__init__(parent)

        self.parent = parent
        self.root = root
        self.controller = controller

        self.entry_strings = []

        self.controller.set_id_info(
            self.root.inventory_type.replace(" ", "_"),
            self.controller.next_id(
                self.controller.database.get_latest_barcode_id(
                    self.root.inventory_type
                )
            ),
        )
        self.controller.set_new_barcode(
            self.controller.get_id_info()[
                self.root.inventory_type.replace(" ", "_")
            ]
        )
        self.root.generate_barcode(self.controller.get_new_barcode())

        table_columns_dict = self.controller.get_database_column_names(
            self.root.table_types["".join(table)]
        )

        # Current tab is accessible from controller class
        if table_columns_dict:
            self.controller.set_tab("".join(table))
        # print(self.controller.get_tab_info())

        # Store all EntryBox widgets
        self.entry_vars = {}

        # *Important* - Store entrybox values (when they change)
        # self.area_1_entries = {}

        # Other
        # Refresh product info area
        for widget in self.root.area_1_frames:
            widget.destroy()

        self.root.area_1_frames.append(self)

        self.area_1_header = customtkinter.CTkLabel(
            self,
            text="".join(table),
            font=customtkinter.CTkFont(size=18, weight="bold"),
        )
        self.area_1_header.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.add_batch_entries(table_columns_dict)

        max_rows_per_column, row, col = self.add_batch_entries(
            table_columns_dict
        )
        # Address Entry
        address_label = customtkinter.CTkLabel(self, text="Address:")
        address_label.grid(row=row, column=col, padx=10, pady=5, sticky="ew")

        sv2 = customtkinter.StringVar()

        # self.entry_strings.append(sv2)
        # sv2.trace(
        #    "w",
        #    lambda *args, name="address", index=entry_count: self.update_key_details(
        #        name, index
        #    ),
        # )

        address_entry = customtkinter.CTkEntry(self, textvariable=sv2)
        address_entry.grid(
            row=row, column=col + 1, padx=10, pady=5, sticky="w"
        )

        # Add address string
        self.entry_vars["address"] = address_entry

        self.add_to_db_checkbox(max_rows_per_column)

    # ADD TO DATABASE LABEL
    def add_to_db_checkbox(self, rows):
        self.add_to_db_var = customtkinter.StringVar(value="off")
        self.db_insertion_checkbox = customtkinter.CTkCheckBox(
            self,
            text="Add to database",  # Label for the checkbox
            variable=self.add_to_db_var,  # Bind to the StringVar to track its state
            onvalue="on",  # The value when the checkbox is checked
            offvalue="off",  # The value when the checkbox is unchecked
            command=self.root.checkbox_changed,  # Function to call when the state changes
        )
        self.db_insertion_checkbox.grid(
            row=rows + 1, column=0, padx=10, pady=10, sticky="sw"
        )

    def add_batch_entries(self, table):
        max_rows_per_column = 7
        row = 1
        col = 0
        entry_count = 0
        for key, v in table.items():
            column_list = table[key]
            formatted_table_columns = self.format_names(column_list)

            for j, column in enumerate(column_list):
                if "id" in column.lower() or "hazard" in column.lower():
                    continue
                elif "quantity" in column.lower():
                    words = column.lower().split("_")
                    words = " ".join(words)
                    formatted_table_columns[j] = words.title()
                elif (
                    "fk" in column.lower()
                ):  # Change fk_location_general_inventory to 'Location'
                    words = column.lower().split("_")
                    words.remove("fk")
                    formatted_table_columns[j] = words[0].title()

                # Create the label for the column
                label = customtkinter.CTkLabel(
                    self, text=formatted_table_columns[j]
                )
                label.grid(row=row, column=col, padx=10, pady=5, sticky="ew")
                # print(formatted_table_columns[j],f"Label Placed Row: {row} | Col: {col}")
                if row == max_rows_per_column - 1:
                    label.grid(row=row, column=col, padx=20, pady=5)

                sv = customtkinter.StringVar()

                self.entry_strings.append(sv)
                sv.trace(
                    "w",
                    lambda *args, name=formatted_table_columns[
                        j
                    ], index=entry_count: self.update_key_details(name, index),
                )

                # Create the entry for the column
                entry = customtkinter.CTkEntry(self, textvariable=sv)

                # Insert default SDS
                if "qr" in formatted_table_columns[j].lower():
                    default_sds = "https://drive.google.com/file/d/1HfsqJG-goraXZHW8OwokIUNG_nVDM_Uz/view"
                    entry.insert(0, default_sds)
                    self.controller.set_qr_code_entry(default_sds)
                entry.grid(
                    row=row, column=col + 1, padx=10, pady=5, sticky="w"
                )

                # print(formatted_table_columns[j],f"Entry Placed Row: {row} | Col: {col+1}")
                if row == max_rows_per_column - 1:
                    entry.grid(row=row, column=col + 1, padx=10, pady=5)

                # Store the entry widget in a dictionary (self.entry_vars)
                self.entry_vars[column] = entry

                row += 1
                entry_count += 1
                if row >= max_rows_per_column:
                    row = 1
                    col += 2

        self.extra_batch_columns(row, col)
        return max_rows_per_column, row, col

    def extra_batch_columns(self, rows, cols):
        self.inventory = self.controller.get_chemical_inventory_stock()
        # Create and place the dropdown (CTkOptionMenu) widget
        self.dropdown = customtkinter.CTkOptionMenu(
            self,
            values=self.inventory,
            fg_color=("gray20", "gray40"),
            button_color=("gray30", "gray50"),
            width=200,
        )

        self.dropdown.grid(row=rows + 2, column=cols, padx=10, pady=5)
        self.dropdown.set("Choose Chemical(s) from Inventory")

    def update_key_details(self, *args):

        # Load StringVar object
        entry_name = args[0]

        str_var = self.entry_strings[args[1]]

        # self.area_1_entries[entry_name] = str_var.get()
        self.controller.set_data_entries(entry_name, str_var.get())
        if "qr" in entry_name.lower():
            self.controller.set_qr_code_entry(str_var.get())

        # Do something with the updated value (for now, just print it)
        # print(f"Entry {args[0]} updated: {str_var.get()}")

        # Set preview text labels
        for key in self.root.preview_key_details.keys():
            for entry in self.controller.get_data_entries().keys():
                # print(f"Is {key.lower()} equal to {entry.lower()}?")
                if key.lower().replace("_", " ") in entry.lower():

                    if key.lower() == "address":
                        if not self.controller.get_data_entries()[entry]:
                            self.root.preview_key_details[key].configure(
                                text=str(f"{self.root.default_address}")
                            )
                        else:
                            self.root.preview_key_details[key].configure(
                                text=str(
                                    f"{self.controller.get_data_entries()[entry]}"
                                )
                            )
                        continue
                    new_key = key.replace("_", " ")
                    if (
                        "product" in new_key
                        and self.controller.get_tab_info()[0]
                        != "general_inventory"
                    ):
                        new_key = "chemical name"
                    self.root.preview_key_details[key].configure(
                        text=str(
                            f"{new_key.title()}: {self.controller.get_data_entries()[entry]}"
                        )
                    )
                if entry.lower() in key.lower().replace("_", " "):
                    new_key = entry.lower().replace("_", " ")
                    if (
                        "product" in new_key
                        and self.controller.get_tab_info()[0]
                        != "general_inventory"
                    ):
                        new_key = "chemical name"
                    self.root.preview_key_details[key].configure(
                        text=str(
                            f"{new_key.title()}: {self.controller.get_data_entries()[entry]}"
                        )
                    )

    # Ex: chemical_inventory -> Chemical Inventory
    def format_names(self, names):
        if type(names) is list:
            return [name.replace("_", " ").title() for name in names]
        elif type(names) is str:
            return names.replace("_", " ").title()
