class Controller:
    def __init__(
        self, Database, PDFGenerator, HazardsPrecautionsData, EntryParser
    ):
        self.view = None

        self.database = Database
        self.pdf_generator = PDFGenerator
        self.hazard_precautions_data = HazardsPrecautionsData
        self.entry_parser = EntryParser

        self.table_entries = {}
        self.area_1_entries = {}
        
        self.cur_tab = {}
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

    #Set chemical/general inventory entries 
    def set_data_entries(self, key, value, table_names):
        # Initialize temp_dict to hold entries for all tables
        temp_dict = {}

        # Preprocess the value for empty input
        value = None if value == '' or value == "" else value

        # Loop through each table in table_names
        for table_name in table_names:
            # Fetch columns for the current table
            columns = self.database.fetch_columns_in_table(table_name)
            
            # Create a dictionary for the current table's entries
            area_1_entries_for_table = {}
            
            # Set the value for the key in area_1_entries before processing the columns
            self.area_1_entries[key] = value

            # Process each column in the current table
            for column in columns:
                # Set value for column based on the key
                if column == key:
                    area_1_entries_for_table[column] = value
                else:
                    # Preserve the existing value if it exists in area_1_entries
                    area_1_entries_for_table[column] = self.area_1_entries.get(column, None)

            # After processing the current table, store the entries in temp_dict
            temp_dict[table_name] = area_1_entries_for_table
        
        #After all tables are processed, store the complete dictionary in self.table_entries
        self.table_entries = temp_dict
        return self.table_entries


    def check_column_exists(self,table,key,value):
        return self.database.column_in_table(key,table)

    def clear_data_entries(self):
        self.area_1_entries = {}
        self.table_entries = {}
    
    def get_data_entries(self):
        return self.table_entries
        #return self.area_1_entries

    def set_tab(self, table_name):
        self.cur_tab = self.get_item_type_tables()[table_name]

    def get_tab_info(self):
        return self.cur_tab
    
    def get_tab_name(self):
        if 'batch' in self.cur_tab[0]:
            for key in self.get_item_type_tables():
                if 'product' in key.lower():
                    return key
        return self.cur_tab[0].replace("_"," ").title()
    
    def set_page_size(self,size):
        self.page_size = size

    def get_page_size(self):
        return self.page_size
    

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

    # Change barcode and qr_code images
    def set_barcode_image(self, file_name):
        self.barcode_png = file_name

    def get_barcode_image(self):
        return self.barcode_png

    def set_qr_code_image(self, file_name):
        self.qr_code_png = file_name

    def get_qr_code_image(self):
        return self.qr_code_png

    def set_get_pdf_path(self, file_dialog_callback):
        self.pdf_generator.save_pdf_callback = file_dialog_callback

    def get_chemical_inventory_stock(self):
        return self.database.fetch_chemicals_stock()

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

    def set_db_insertion(self,bool):
        self.db_insertion = bool
        if bool:
            user_entries = self.get_data_entries()
            if user_entries:
                for table in user_entries.keys():
                    expected = self.entry_parser.convert_value_types(user_entries[table],table)
                    conversion = self.entry_parser.convert_to_types(user_entries[table],expected)
                    if isinstance(conversion, dict):
                        # update table_entries with converted version
                        self.table_entries[table] = conversion
                        #self.table_entries
                    elif conversion: 
                        self.view.data_error_message(conversion)
                        return None
                    
                # Table entries dictionary now has correct types 
                # Pass this directly to SQL query for db insertion
                data_entries = self.get_data_entries()

                print("Add to database (Active): ")
                for outer_key, inner_dict in data_entries.items():
                    print(f"{outer_key}:")
                    for inner_key, value in inner_dict.items():
                        print(f"  - {inner_key}: {value}")
            else:
                self.view.data_warning_message("No values inserted in (Press Enter)")
                self.db_insertion = False
                self.view.area_1.add_to_db_var.set(value="off")


    def add_to_database(self, table, user_entries):
        if user_entries:
            user_entries = self.assort_columns(table, user_entries)
            print(f"Attempting to add user_entries to {table}..")
            self.database.insert_data_into_db(table, user_entries) # Important - Passes user entries to PostgreSQL
        else:
            print(f"No valid entries to insert ({table})")
    

    def next_id(self,tab_name):
        new_id = self.database.get_latest_barcode_id(tab_name)
        if new_id is None:
            self.view.data_error_message("Failed to fetch product id")
        return new_id
    
    #Get new barcode id
    def next_id_str(self,id_str):
        try:
            prefix = id_str[:2]  #Ex: 'BN'
            number_str = id_str[2:]
            new_number_str = f"{int(number_str) + 1:010d}"
            return prefix + new_number_str
        except:
            self.view.data_error_message("Failed to fetch product id")
            return None


    # def on_submission(self):
    #     item_frame_container = self.view.item_frame_container

    #     selected_type = item_frame_container.item_type_var.get()

    #     selected_frame = item_frame_container.item_type_frames[selected_type]

    #     table_names = selected_frame.table_names
    #     table_cols_dict = self.get_database_column_names(table_names)

    #     # 1) Query IDs for the selected item and generate one that is 1 higher
    #     # 2) Somehow generate a dynamic query that inserts however many parameters
    #     # you have into the correct database tables
    #     # 3) take that information and generate the PDF and store it

    #     # if the tickbox on the corresponding frame is ticked, then do database things
    #     # if its not then don't
    #     if selected_frame.checkbox_var.get():
    #         print("would submit to the database")

    #     # maybe gather the data here but you should do the actual query in database
    #     for table in table_cols_dict.values():
    #         for col in table:
    #             print(col)
    #             if "id" in col.lower() or "hazard" in col.lower():
    #                 continue
    #             print(selected_frame.entry_vars[col].get())

    #         #
    #         selected_hazards = self.get_selected_hazards()
    #         selected_precautions = self.get_selected_precautions()

    #     self.pdf_generator.generate_pdf(
    #         details, selected_hazards, selected_precautions
    #     )

    #     self.view.display_success("PDF generated successfully!")

    def add_id(self,entries):
        for table in entries:
            for item in entries[table].keys():
                if 'id' in item:
                    entries[table][item] = self.get_new_barcode()
        return entries

    def on_submission2(self):

        cur_tab = self.get_tab_info()[0]

        entries = self.get_data_entries()
        entries = self.add_id(entries) #Add ID to tables
        
        
        # Hazards and Precautions
        if "general" not in cur_tab:
            selected_hazards = self.get_selected_hazards()
            selected_precautions = self.get_selected_precautions()

        if self.db_insertion:
            for key in entries:
                
                self.add_to_database(key, entries[key])
                
                #self.view.data_error_message(conversion)
                #self.db_insertion = False

    def get_database_column_names(self, table):
        return self.database.fetch_column_names(table)

    def set_view(self, view):
        self.view = view
