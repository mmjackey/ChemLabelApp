import os
import sys


class Controller:
    def __init__(self, Database, HazardsPrecautionsData, EntryParser):
        self.view = None

        self.database = Database
        self.hazard_precautions_data = HazardsPrecautionsData
        self.entry_parser = EntryParser

        self.hazard_diamonds = self.hazard_precautions_data.HAZARD_DIAMONDS
        self.qr_code_entry = {}
        self.page_size = 0
        self.barcode_final = ""

        self.barcode_png = None
        self.qr_code_png = None

        self.id_info = {}

        self.db_insertion = False

        self.converted_entries = {}

    def get_item_type_tables(self):
        return self.database.get_inventory_table_types()

    def get_hazard_classes_dict(self):
        return self.hazard_precautions_data.HAZARD_CLASSES

    def get_precaution_classes_dict(self):
        return self.hazard_precautions_data.PRECAUTION_CLASSES

    def get_hazard_diamonds_dict(self):
        return self.hazard_precautions_data.HAZARD_DIAMONDS

    def get_hazards(self, hazard_type):
        return self.hazard_precautions_data.HAZARD_CLASSES.get(hazard_type, [])

    def get_selected_hazards(self):
        return self.hazard_precautions_data.selected_hazards

    def append_hazard_variables(self, var, hazard):
        self.hazard_precautions_data.selected_hazards.append((var, hazard))

    def get_selected_precautions(self):
        return self.hazard_precautions_data.selected_precautions

    def append_precautions_variables(self, var, precaution):
        self.hazard_precautions_data.selected_precautions.append(
            (var, precaution)
        )

    def get_precautions(self, precaution_type):
        return self.hazard_precautions_data.PRECAUTION_CLASSES.get(
            precaution_type, []
        )

    def append_diamond_variables(self, var, hazard, image):
        self.hazard_precautions_data.diamond_vars.append((var, hazard, image))

    def get_diamond_vars(self):
        return self.hazard_precautions_data.diamond_vars

    # Get hazards, precautions, and diamonds
    def get_haz_prec_diamonds(self):
        return (
            self.get_selected_hazards() + self.get_selected_precautions()
        )  # + self.get_diamond_vars()

    def set_page_size(self, size):
        self.page_size = size

    def get_page_size(self):
        return self.page_size

    # Get new barcode id
    def next_id(self, id_str):
        prefix = id_str[:2]  # Ex: 'BN'
        number_str = id_str[2:]
        new_number_str = f"{int(number_str) + 1:010d}"
        return prefix + new_number_str

    def set_qr_code_entry(self, qr_code_str):
        self.qr_code_entry = qr_code_str

    def get_qr_code_entry(self):
        return self.qr_code_entry

    def set_new_barcode(self, barcode_str):
        self.barcode_final = barcode_str

    def get_new_barcode(self):
        return self.barcode_final

    def set_id_info(self, table_type, id_str):
        self.id_info = {}
        self.id_info[table_type] = id_str

    def get_id_info(self):
        return self.id_info

    def get_path(self, relative_path):
        if getattr(sys, "frozen", False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    # Change barcode and qr_code images
    def set_barcode_image(self, file_name):
        self.barcode_png = self.get_path(file_name)

    def get_barcode_image(self):
        return self.barcode_png

    def set_qr_code_image(self, file_name):
        self.qr_code_png = self.get_path(file_name)

    def get_qr_code_image(self):
        return self.qr_code_png

    def set_get_pdf_path(self, file_dialog_callback):
        self.pdf_generator.save_pdf_callback = file_dialog_callback

    def get_chemical_inventory_stock(self):
        return self.database.fetch_chemicals_stock()

    def clear_tab_entries(self, tab):
        tab_entries = self.database.tab_entries
        for table, column in tab_entries[tab].items():
            tab_entries[tab][table].clear()

    def add_tab_specific_column(self, tab, column, value):
        self.database.tab_entries[tab][column] = value

    def add_tab_entries(self, tab, dictionary):
        self.database.tab_entries[tab] = dictionary

    def retrieve_tab_entries(self, tab):
        return self.database.tab_entries[tab]

    def fix_columns(self, the_dict, table):
        table_def = table.replace("_", " ").title()
        if "batch" in table_def.lower():
            table_def = "Product Inventory (Batch Process)"
        table_columns_dict = self.get_database_column_names(
            self.get_item_type_tables()[table_def]
        )
        user_entries = the_dict
        total_entries = {}
        normalized_entries = {}

        stop_early = False
        for table, db_column_list in table_columns_dict.items():
            # print("New table: ", table)
            for key, value in user_entries.items():
                if "batch" in table.lower():
                    stop_early = True
                # Normalize user column name (spaces to underscores, lowercase)
                normalized_key = key.replace(" ", "_").lower()

                # Check for exact match first
                matched = False
                for db_col in db_column_list:
                    normalized_db_col = db_col.replace(" ", "_").lower()

                    if normalized_key == normalized_db_col:  # Exact match
                        normalized_entries[db_col] = value
                        matched = True
                        break

                if not matched:
                    for db_col in db_column_list:
                        normalized_db_col = db_col.replace(" ", "_").lower()
                        if normalized_key in normalized_db_col:
                            if key in normalized_entries:
                                del normalized_entries[key]

                            normalized_entries[db_col] = value
                            print(
                                f"Renamed '{key}' to '{db_col}' based on partial match."
                            )
                            break

            # for key in normalized_entries:
            #     for k, sub_dict in total_entries.items():
            #         # Make sure sub_dict is a dictionary before trying to delete a key
            #         if isinstance(sub_dict, dict) and key in sub_dict:
            #             del sub_dict[key]

            total_entries[table] = normalized_entries
            if stop_early:
                break

        valid_entries = normalized_entries
        return valid_entries

    def assort_columns(self, table_name, user_entries):
        # Get the column order from the database
        column_order = self.database.get_column_order(table_name)

        # Reorder user entries based on column order
        sorted_entries = {
            key: user_entries[key]
            for key in column_order
            if key in user_entries
        }

        return sorted_entries

    def set_db_insertion(self, value, current_tab):
        # Check entries
        self.db_insertion = value

    def add_to_database(self, tab, id):
        tables = self.retrieve_tab_entries(tab)
        for table, columns in tables.items():
            types = self.database.get_column_types(table)
            columns_list = []
            entries = []
            if "additional" in table:
                entries
                continue
            for column, entry in columns.items():
                columns_list.append(column)
                if "id" in column:
                    entries.append(f"'{id}'")
                    continue
                elif "hazard" in column:
                    entries.append("NULL")
                    continue
                elif entry.get() is None or entry.get() == "":
                    entries.append("NULL")
                else:
                    entries.append(f"'{entry.get()}'")

            self.database.insert_data_into_db(table, columns_list, entries)

    def on_submission2(self, table, current_tab):
        # Details from tab
        selected_details = {}
        latest_id = self.database.get_latest_barcode_id(table)

        # Create new barcode id
        next_id = self.next_id(latest_id)
        self.set_new_barcode(next_id)

        # QR Code
        details3 = self.get_qr_code_entry()

        # Page Size
        details4 = "Landscape"  # self.get_page_size()

        selected_details["barcode_input"] = next_id
        selected_details["qr_code_input"] = details3
        selected_details["page_size"] = details4

        # Hazards and Precautions
        if current_tab != "general_inventory":
            selected_hazards = self.get_selected_hazards()
            selected_precautions = self.get_selected_precautions()

        if self.db_insertion:
            self.add_to_database(current_tab, next_id)

    def get_database_column_names(self, table):
        return self.database.fetch_column_names(table)

    def set_view(self, view):
        self.view = view
