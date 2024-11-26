class Controller:
    def __init__(self, Database, PDFGenerator, HazardsPrecautionsData,EntryParser):
        self.view = None

        self.database = Database
        self.pdf_generator = PDFGenerator
        self.hazard_precautions_data = HazardsPrecautionsData
        self.entry_parser = EntryParser
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

    #Get hazards, precautions, and diamonds
    def get_haz_prec_diamonds(self):
        return self.get_selected_hazards() + self.get_selected_precautions() #+ self.get_diamond_vars()

    #Set chemical/general inventory entries 
    def set_data_entries(self,key,value):
        self.area_1_entries[key] = value


    def clear_data_entries(self):
        self.area_1_entries = {}
    
    def get_data_entries(self):
        return self.area_1_entries

    def set_tab(self,table_name):
        self.cur_tab = self.get_item_type_tables()[table_name]
    
    def get_tab_info(self):
        return self.cur_tab
    
    def set_page_size(self,size):
        self.page_size = size
    
    def get_page_size(self):
        return self.page_size
    
    #Get new barcode id
    def next_id(self,id_str):
        prefix = id_str[:2]  #Ex: 'BN'
        number_str = id_str[2:]
        new_number_str = f"{int(number_str) + 1:010d}"
        return prefix + new_number_str

    def set_qr_code_entry(self,qr_code_str):
        self.qr_code_entry = qr_code_str

    def get_qr_code_entry(self):
        return self.qr_code_entry
    
    def set_new_barcode(self,barcode_str):
        self.barcode_final = barcode_str

    def get_new_barcode(self):
        return self.barcode_final
    
    def set_id_info(self,table_type, id_str):
        self.id_info = {}
        self.id_info[table_type] = id_str
    
    def get_id_info(self):
        return self.id_info
    
    #Change barcode and qr_code images
    def set_barcode_image(self,file_name):
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

    def fix_columns(self,the_dict,table):
        table_def = table.replace("_"," ").title()
        if "batch" in table_def.lower():
            table_def ="Product Inventory (Batch Process)"
        table_columns_dict = self.get_database_column_names(
            self.get_item_type_tables()[table_def]
        )
        user_entries = the_dict
        total_entries = {}
        normalized_entries = {}
        
        stop_early = False
        for table, db_column_list in table_columns_dict.items():
            #print("New table: ", table)
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
                            print(f"Renamed '{key}' to '{db_col}' based on partial match.")
                            break
                
            # for key in normalized_entries:
            #     for k, sub_dict in total_entries.items():
            #         # Make sure sub_dict is a dictionary before trying to delete a key
            #         if isinstance(sub_dict, dict) and key in sub_dict:
            #             del sub_dict[key]
            
            total_entries[table] = normalized_entries
            if stop_early: break

            
        valid_entries = normalized_entries
        return valid_entries
        
    def assort_columns(self, table_name, user_entries):
        # Get the column order from the database
        column_order = self.database.get_column_order(table_name)

        # Reorder user entries based on column order
        sorted_entries = {key: user_entries[key] for key in column_order if key in user_entries}

        return sorted_entries

    def set_db_insertion(self,bool):
        #print("db_insertion set to: ", str(bool))
        #Check entries
        self.db_insertion = bool
        if bool:
            self.entry_parser
            cur_table = self.get_tab_info()[0]
            user_entries = self.fix_columns(self.get_data_entries(),cur_table)
            user_entries = {key: value for key, value in user_entries.items() if value != ""}
            expected = self.entry_parser.convert_value_types(user_entries,cur_table)

            conversion = self.entry_parser.convert_to_types(user_entries,expected_types=expected)
            if isinstance(conversion, dict):
                for name,i in conversion.items():
                    self.converted_entries = conversion
                    #print(f"{name} : {type(i)}")
                    pass
            elif conversion:
                #print(conversion)
                self.view.data_error_message(conversion)

                self.db_insertion = False
            #print(self.database.check_column_data_types(user_entries, cur_table))

    def add_to_database(self,table,details):
        stop_early = False
        table_def = table.replace("_"," ").title()
        if "batch" in table_def.lower():
            table_def ="Product Inventory (Batch Process)"
        table_columns_dict = self.get_database_column_names(
            self.get_item_type_tables()[table_def]
        )
        user_entries = details
        db_columns = table_columns_dict
        normalized_entries = {}
        
        for table in db_columns:
            #print(f"Insert into {table}")
            if "batch" in table.lower():
                stop_early = True
            for key, value in user_entries.items():
                normalized_key = key.replace(" ", "_").lower()  # Convert spaces to underscores and make lowercase
                
                if normalized_key in db_columns[table]:
                    normalized_entries[normalized_key] = value
            
            valid_entries = normalized_entries
            if valid_entries:  # Only insert if there are valid entries
                valid_entries = self.assort_columns(table,valid_entries)
                print(valid_entries)
                self.database.insert_data_into_db(table,valid_entries)
            else:
                print("No valid entries to insert.")
            if stop_early: break
    
    def on_submission(self):
        item_frame_container = self.view.item_frame_container

        selected_type = item_frame_container.item_type_var.get()

        selected_frame = item_frame_container.item_type_frames[selected_type]

        table_names = selected_frame.table_names
        table_cols_dict = self.get_database_column_names(table_names)

        # 1) Query IDs for the selected item and generate one that is 1 higher
        # 2) Somehow generate a dynamic query that inserts however many parameters
        # you have into the correct database tables
        # 3) take that information and generate the PDF and store it

        # if the tickbox on the corresponding frame is ticked, then do database things
        # if its not then don't
        if selected_frame.checkbox_var.get():
            print("would submit to the database")

        # maybe gather the data here but you should do the actual query in database
        for table in table_cols_dict.values():
            for col in table:
                print(col)
                if "id" in col.lower() or "hazard" in col.lower():
                    continue
                print(selected_frame.entry_vars[col].get())

            #
            selected_hazards = self.get_selected_hazards()
            selected_precautions = self.get_selected_precautions()

        self.pdf_generator.generate_pdf(
            details, selected_hazards, selected_precautions
        )

        self.view.display_success("PDF generated successfully!")
    
    def on_submission2(self):

        cur_tab = self.get_tab_info()[0]
        details1 = self.area_1_entries

        #Details from tab
        selected_details = {}
        selected_details2 = {}
        selected_details3 = {}
        selected_details4 = {}
        if cur_tab == "chemical_details":
            selected_data = ['chemical_name', 'volume', 'concentration','qr_code']
            for key in details1.keys():
                if key.lower().replace(" ","_") in [x.lower() for x in selected_data]:
                    key_index = key.lower()
                    if "qr" in key.lower():
                        key_index = "qr_code"
                    selected_details[key_index] = details1[key]
                selected_details2[key_index] = details1[key]
        if cur_tab == "batch_inventory":
            selected_data = ['start_vol', 'current_volume', 'production','qr_code']
            for key in details1.keys():
                if key.lower().replace(" ","_") in [x.lower() for x in selected_data]:
                    key_index = key.lower()
                    if "qr" in key.lower():
                        key_index = "qr_code"
                    selected_details[key_index] = details1[key]
                selected_details2[key_index] = details1[key]
        if cur_tab == "general_inventory":
            selected_data1 = ['quantity', 'location', 'production','qr_code']
            selected_data2 = ['product_name','product_description','vendor_sku','hazard_details','model_number','vendor_name','category', 'image_url','order_url']
            for key in details1.keys():
                if key.lower().replace(" ","_") in [x.lower() for x in selected_data1]:
                    key_index = key.lower()
                    if "qr" in key.lower():
                        key_index = "qr_code"
                    selected_details[key_index] = details1[key]
                selected_details2[key_index] = details1[key]
                if key.lower().replace(" ","_") in [x.lower() for x in selected_data2]:
                    key_index = key.lower()
                    if "qr" in key.lower():
                        key_index = "qr_code"
                    selected_details3[key_index] = details1[key]
                selected_details4[key_index] = details1[key]

        #Create new barcode id
        details2 = self.next_id(self.database.get_latest_barcode_id(self.get_tab_info()[0]))
        self.set_new_barcode(details2)

        #QR Code
        details3 = self.get_qr_code_entry()

        #Page Size
        details4 = "Landscape" #self.get_page_size()

    
        selected_details["barcode_input"] = details2
        selected_details["qr_code_input"] = details3
        selected_details["page_size"] = details4
        
        selected_details2 = self.fix_columns(self.get_data_entries(),cur_tab)

        if self.converted_entries:
            self.converted_entries["id"] = details2
        selected_details2["id"] = details2

        #Hazards and Precautions
        if cur_tab != "general_inventory":
            selected_hazards = self.get_selected_hazards()
            selected_precautions = self.get_selected_precautions()

        if self.db_insertion: 
            if self.converted_entries:
                expected = self.entry_parser.convert_value_types(self.converted_entries,cur_tab)
                conversion = self.entry_parser.convert_to_types(self.converted_entries,expected_types=expected)
            else:
                expected = self.entry_parser.convert_value_types(selected_details2,cur_tab)
                conversion = self.entry_parser.convert_to_types(selected_details2,expected_types=expected)
            if isinstance(conversion, dict):
                print(conversion) 
                self.add_to_database(self.get_tab_info()[0],self.converted_entries)
                for name,i in conversion.items():
                    #print(f"{name} : {type(i)}")
                    pass
            elif conversion:
                self.view.data_error_message(conversion)
                self.db_insertion = False
            
           

    def get_database_column_names(self, table):
        return self.database.fetch_column_names(table)

    def set_view(self, view):
        self.view = view
