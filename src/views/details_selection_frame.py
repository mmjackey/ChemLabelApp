import customtkinter


class DetailSelectFrame(customtkinter.CTkFrame):
    def __init__(self, parent, controller, table):
        super().__init__(parent)

        self.parent = parent
        self.controller = controller

        self.entry_strings = []

        self.controller.set_id_info(
            self.parent.inventory_type.replace(" ", "_"),
            self.controller.next_id(
                self.controller.database.get_latest_barcode_id(
                    self.parent.inventory_type
                )
            ),
        )
        self.controller.set_new_barcode(
            self.controller.get_id_info()[
                self.parent.inventory_type.replace(" ", "_")
            ]
        )
        self.parent.generate_barcode(self.controller.get_new_barcode())

        table_columns_dict = self.controller.get_database_column_names(
            self.parent.table_types["".join(table)]
        )

        # Current tab is accessible from controller class
        if table_columns_dict:
            self.parent.current_tab = "".join(table)

        # Store all EntryBox widgets
        self.entry_tables = {
            key: {item: None for item in value}
            for key, value in table_columns_dict.items()
        }
        self.entry_tables["additional"] = {}

        self.trace_ids = {}

        self.area_1_header = customtkinter.CTkLabel(
            self,
            text="".join(table),
            font=customtkinter.CTkFont(size=18, weight="bold"),
        )
        self.area_1_header.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        max_rows_per_column, row, col = self.add_batch_entries(
            table_columns_dict
        )

        # Address Entry
        address_label = customtkinter.CTkLabel(self, text="Address:")
        address_label.grid(row=row, column=col, padx=10, pady=5, sticky="ew")

        sv2 = customtkinter.StringVar()

        self.entry_strings.append(sv2)
        trace = sv2.trace_add(
            "write",
            lambda *args, name="address", index=row: self.update_key_details(
                name, index
            ),
        )

        self.trace_ids[trace] = (sv2, "write")
        address_entry = customtkinter.CTkEntry(self, textvariable=sv2)
        address_entry.grid(
            row=row, column=col + 1, padx=10, pady=5, sticky="w"
        )
        # Add address string
        self.entry_tables["additional"]["address"] = address_entry

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
            command=self.parent.checkbox_changed,  # Function to call when the state changes
        )
        self.db_insertion_checkbox.grid(
            row=rows + 1, column=0, padx=10, pady=10, sticky="sw"
        )

    def add_batch_entries(self, table):
        max_rows_per_column = 7
        row = 1
        col = 0
        entry_count = 0
        current_tab = self.parent.current_tab
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
                if row == max_rows_per_column - 1:
                    label.grid(row=row, column=col, padx=20, pady=5)

                sv = customtkinter.StringVar()

                # Create the entry for the column
                entry = customtkinter.CTkEntry(self, textvariable=sv)

                # Insert default SDS
                if column == "qr_code":
                    default_sds = "https://drive.google.com/file/d/1HfsqJG-goraXZHW8OwokIUNG_nVDM_Uz/view"
                    sv.set(default_sds)
                    self.controller.set_qr_code_entry(default_sds)

                entry.grid(
                    row=row, column=col + 1, padx=10, pady=5, sticky="w"
                )

                if row == max_rows_per_column - 1:
                    entry.grid(row=row, column=col + 1, padx=10, pady=5)
                # Store the entry widget in a dictionary (self.entry_vars)
                self.entry_tables[key][column] = entry

                self.entry_strings.append(sv)
                trace = sv.trace_add(
                    "write",
                    lambda *args, sv=sv, tab=current_tab, name=column, table=key: self.update_key_details(
                        name, table, tab, sv
                    ),
                )
                self.trace_ids[trace] = (sv, "write")

                row += 1
                entry_count += 1
                if row >= max_rows_per_column:
                    row = 1
                    col += 2
        self.controller.add_tab_entries(
            self.parent.current_tab, self.entry_tables
        )
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

    def update_key_details(self, name, table, tab, sv):
        # Load StringVar object
        # str_var = self.entry_strings[args[1]]

        # self.area_1_entries[entry_name] = str_var.get()
        # self.controller.set_data_entries(entry_name, str_var.get())

        if "qr_code" in name.lower():
            self.controller.set_qr_code_entry(sv.get())

        # Set preview text labels
        self.parent.preview_key_details[name].configure(
            text=str(f"{sv.get()}")
        )
        #            if key.lower() == "address":
        #                if not self.controller.get_data_entries()[entry]:
        #                    self.parent.preview_key_details[key].configure(
        #                        text=str(f"{self.parent.default_address}")
        #                    )
        #                else:
        #                    self.parent.preview_key_details[key].configure(
        #                        text=str(
        #                            f"{self.controller.get_data_entries()[entry]}"
        #                        )
        #                    )
        #                continue
        #            new_key = key.replace("_", " ")
        #            if (
        #                "product" in new_key
        #                and self.controller.get_tab_info()[0]
        #                != "general_inventory"
        #            ):
        #                new_key = "chemical name"
        #            self.parent.preview_key_details[key].configure(
        #                text=str(
        #                    f"{new_key.title()}: {self.controller.get_data_entries()[entry]}"
        #                )
        #            )
        #        if entry.lower() in key.lower().replace("_", " "):
        #            new_key = entry.lower().replace("_", " ")
        #            if (
        #                "product" in new_key
        #                and self.controller.get_tab_info()[0]
        #                != "general_inventory"
        #            ):
        #                new_key = "chemical name"
        #            self.parent.preview_key_details[key].configure(
        #                text=str(
        #                    f"{new_key.title()}: {self.controller.get_data_entries()[entry]}"
        #                )
        #            )

    def destroy_traces(self):
        for trace_id, (var, mode) in self.trace_ids.items():
            for ti in var.trace_vinfo():
                var.trace_vdelete(*ti)
        self.trace_ids.clear()
        super().destroy()

    # Ex: chemical_inventory -> Chemical Inventory
    def format_names(self, names):
        if type(names) is list:
            return [name.replace("_", " ").title() for name in names]
        elif type(names) is str:
            return names.replace("_", " ").title()
