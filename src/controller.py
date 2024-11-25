class Controller:
    def __init__(self, Database, PDFGenerator, HazardsPrecautionsData):
        self.view = None

        self.database = Database
        self.pdf_generator = PDFGenerator
        self.hazard_precautions_data = HazardsPrecautionsData
        self.area_1_entries = {}
        self.cur_tab = {}
        self.hazard_diamonds = self.hazard_precautions_data.HAZARD_DIAMONDS
        self.qr_code_entry = {}
        self.page_size = 0
        self.barcode_final = ""

        self.barcode_png = None
        self.qr_code_png = None

    def get_item_type_tables(self):
        return self.database.item_type_tables

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
        if cur_tab == "chemical_details":
            selected_data = ['chemical_name', 'volume', 'concentration','qr_code']
            for key in details1.keys():
                print(key.lower().replace(" ","_"))
                if key.lower().replace(" ","_") in [x.lower() for x in selected_data]:
                    key_index = key.lower()
                    if "chemical" in key.lower():
                        key_index = "name"
                    if "qr" in key.lower():
                        key_index = "qr_code_input"
                    selected_details[key_index] = details1[key]

        #Create new barcode id
        details2 = self.next_id(self.database.get_latest_barcode_id())
        self.set_new_barcode(details2)

        #QR Code
        details3 = self.get_qr_code_entry()

        #Page Size
        details4 = "Landscape" #self.get_page_size()

        selected_details["barcode_input"] = details2
        selected_details["qr_code_input"] = details3
        selected_details["page_size"] = details4
        print(selected_details)
        
        #Hazards and Precautions
        if cur_tab != "general_inventory":
            selected_hazards = self.get_selected_hazards()
            selected_precautions = self.get_selected_precautions()

        # self.pdf_generator.generate_pdf(
        #     selected_details, selected_hazards, selected_precautions
        # )
        # item_frame_container = self.view.item_frame_container

        # selected_type = item_frame_container.item_type_var.get()

        # selected_frame = item_frame_container.item_type_frames[selected_type]

        # table_names = selected_frame.table_names
        # table_cols_dict = self.get_database_column_names(table_names)

        # # 1) Query IDs for the selected item and generate one that is 1 higher
        # # 2) Somehow generate a dynamic query that inserts however many parameters
        # # you have into the correct database tables
        # # 3) take that information and generate the PDF and store it

        # # if the tickbox on the corresponding frame is ticked, then do database things
        # # if its not then don't
        # if selected_frame.checkbox_var.get():
        #     print("would submit to the database")

        # # maybe gather the data here but you should do the actual query in database
        # for table in table_cols_dict.values():
        #     for col in table:
        #         print(col)
        #         if "id" in col.lower() or "hazard" in col.lower():
        #             continue
        #         print(selected_frame.entry_vars[col].get())

        #     #
        #     selected_hazards = self.get_selected_hazards()
        #     selected_precautions = self.get_selected_precautions()

        # self.pdf_generator.generate_pdf(
        #     details, selected_hazards, selected_precautions
        # )

        #self.view.display_success("PDF generated successfully!")

    def get_database_column_names(self, table):
        return self.database.fetch_column_names(table)

    def set_view(self, view):
        self.view = view
