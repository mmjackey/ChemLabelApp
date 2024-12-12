import customtkinter
import tkinter as tk
from tkinter import ttk

from PIL import Image, ImageTk
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
        self.preview_label_frame = customtkinter.CTkFrame(self, fg_color="#FAF9F6", corner_radius=0)
        self.preview_label_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)

        self.hazard_preview_font_size = 13
        self.details_preview_font_size = 13

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
            #self.root.area_5.text_box.configure(width=400)
            # label = customtkinter.CTkLabel(
            #     self.preview_label_frame,
            #     text="Landscape Mode",
            #     font=("Arial", 16),
            # )
            self.preview_label_frame.grid(
                row=2, column=0, sticky="nsew", padx=10, pady=10
            )
            
            page_size = landscape(A4)
            self.controller.set_page_size(page_size)
        elif selection == "Portrait":
            #self.root.area_5.text_box.configure(width=200)
            self.preview_label_frame.configure(width=200, height=400)  # Set portrait dimensions
            label = customtkinter.CTkLabel(self.preview_label_frame, text="Portrait Mode", font=("Arial", 16))
            self.preview_label_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)

            page_size = A4
            self.controller.set_page_size(page_size)
        self.preview_label_frame.grid_propagate(False)
        self.create_preview_label(self.orientation_option_menu.get(),tab=self.controller.get_tab_info()[0])
    
    def create_preview_label(self, selection, tab=None, hazards=True): 
        if selection == "Landscape":
            # Configure grid columns
            for col in range(4):
                weight = 1 if col < 3 else 0
                self.preview_label_frame.grid_columnconfigure(col, weight=weight)
            
            # Logo Label
            self.logo_label = self.create_image_label(AppConfig.LOGO_PREVIEW, (160, 40), row=0, column=0, padx = 10, sticky="w")
            
            # Barcode Preview Label
            self.barcode_photo_prev = customtkinter.CTkImage(dark_image=Image.open(AppConfig.BARCODE), size=(60,60))
            self.barcode_label_prev = self.create_image_label("barcode.png", (60, 60), row=0, column=1, padx=(0, 15), sticky="w")
            self.barcode_label_prev.configure(image=self.barcode_photo_prev)

            # QR Code Preview Label
            self.qr_code_label = self.create_image_label("resources/images/qr_code.png", (80, 80), row=0, column=2, sticky="e")
            
            # Reset key details if they exist
            self.clear_preview_key_details()

            # Create and filter table columns based on tab selection
            
            self.add_details(tab)

            # Key details Textbox
            self.details_preview_textbox = customtkinter.CTkTextbox(
                self.preview_label_frame, height=100, width=275, fg_color="transparent", text_color="black", wrap="word"
            )
            self.details_preview_textbox.grid(row=3, column=0, columnspan=1, padx=2, sticky="ew")
            #self.details_preview_textbox.bind("<KeyRelease>", lambda event: self.adjust_font_size(self.details_preview_textbox))

            

            # Hazards/Precautions Textbox
            self.hazards_preview_textbox = customtkinter.CTkTextbox(
                self.preview_label_frame, height=110, width=275, fg_color="transparent", text_color="black", wrap="word"
            )
            self.hazards_preview_textbox.grid(row=4, column=0, columnspan=1, padx=2, sticky="ew")
            self.hazards_preview_textbox.bind("<KeyRelease>", lambda event: self.adjust_font_size(self.hazards_preview_textbox))
            if hazards or self.controller.get_tab_info()[0] != "general_inventory":
                self.hazards_preview_textbox.insert(tk.END, self.root.stored_preview_text)
                self.hazards_preview_textbox.cget("font").configure(size=self.hazard_preview_font_size)
                self.hazards_preview_textbox.configure(font=self.hazards_preview_textbox.cget("font"))
            else:
                self.hazards_preview_textbox.delete("1.0", tk.END)
            
            # Diamonds preview frame
            self.create_diamonds_frame()

            # Address label
            self.address_label = customtkinter.CTkLabel(
                self.preview_label_frame, text=self.root.default_address, text_color="black", anchor="w", wraplength=300, fg_color="transparent"
            )
            self.address_label.grid(row=5, column=0, columnspan=1, padx=5, pady=(10,0), sticky="ew")
            

            self.root.preview_key_details["address"] = self.address_label

        self.preview_label_frame.grid_rowconfigure(1, weight=0)
        self.preview_label_frame.grid_columnconfigure(2, weight=1)  # Empty column for spacing
        self.preview_label_frame.grid_rowconfigure(4,weight=1)
        if self.controller.get_tab_info()[0] != "general_inventory":
            self.add_hazard_symbols(self.root.stored_diamonds)

    def adjust_font_size(self,textbox):
        self.root.update()
        # # Set initial font size
        # print(textbox.cget("font")._size)
        # font_size = textbox.cget("font")._size
        # max_font_size = font_size
        # min_font_size = 6

        # # Get the dimensions of the textbox
        # textbox_width = 275
        # textbox_height = textbox.winfo_height()

        # # Get the text content from the textbox
        # text_content = textbox.get("1.0", "end-1c")
        # text_length = len(text_content)
        # # If the text exceeds the height or width, reduce the font size
        # #chars_per_line = int(275 // char_width)
        # print(f"Font Size/Character width: {textbox.cget('font')._size},{self.hazard_preview_char_width}")
        # print(f"Textbox fits {self.hazard_preview_char_width} characters")
        # print(f"Character Count: {text_length}")
        # if text_length > self.hazard_preview_char_width * 2:
        #     font_size -= 1  # You can adjust the calculation as needed
        #     self.hazard_preview_char_width *= 2
        #     font_size = max(font_size, min_font_size)  # Ensure font size doesn't go too small
        # else:
        #     font_size = font_size  # Default font size
        # text = textbox.get("1.0", "end-1c")

        # Apply the font size to the textbox
        # print(f"New font: {textbox.cget("font"),font_size}")
        textbox.cget("font").configure(size=self.hazard_preview_font_size)
        textbox.configure(font=textbox.cget("font"))

    def create_image_label(self, image_path, size, row, column, sticky, padx=(0, 0)):
        """Helper function to create image labels with custom size."""
        image = Image.open(image_path)
        image_preview = customtkinter.CTkImage(dark_image=image, size=size)
        label = customtkinter.CTkLabel(self.preview_label_frame, image=image_preview, text="")
        label.grid(row=row, column=column, padx=padx, sticky=sticky)
        return label

    def update_preview_box(self,args):
        text=args[0]
        hazard_symbols=args[1]
        self.root.area_4.hazards_preview_textbox.delete("1.0", tk.END)  # Clear the existing text
        self.root.area_4.hazards_preview_textbox.insert(tk.END, text)  # Insert the updated text
        self.root.stored_preview_text = text
        
        self.root.area_4.add_hazard_symbols(hazard_symbols)
    

    def clear_preview_key_details(self):
        """Clear any existing preview key details."""
        if self.root.preview_key_details.items():
            for widget in self.root.preview_key_details.values():
                widget.destroy()
            self.root.preview_key_details = {}
    
    def add_details(self,table):
        pass

    def create_table_columns(self, table, row, max_rows_per_column):
        table_columns_dict = self.controller.get_database_column_names(self.root.table_types[''.join(table)])

        #print("Preview: ", table_columns_dict)
        #print("Preview: ", self.controller.get_data_entries())
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
        column_lower = column.lower()
        if "id" in column_lower or "hazard" in column_lower:
            return True
        if "quantity" in column_lower:
            return True
        if "fk" in column_lower:
            return True
        if key == "chemical_inventory" and column_lower not in ['date', 'volume']:
            return True
        # if key == "chemical_details" and column_lower not in ['chemical_name', 'volume', 'concentration']:
        #     return True
        if key == "general_product" and self.controller.get_tab_info()[0] != "general_inventory" and "product" in column_lower:
            return True
        if key == "general_inventory" and column_lower not in ['product_name', 'fk_location_general_inventory', 'product_description']:
            return True
        return False

    def create_diamonds_frame(self):
        """Create and configure the diamonds preview frame."""
        self.diamonds_preview_frame = customtkinter.CTkFrame(
            self.preview_label_frame, width=120, height=120, fg_color="transparent"
        )
        self.diamonds_preview_frame.place(x=290, y=160)
        self.diamonds_preview_frame.grid_propagate(False)
        #self.diamonds_preview_frame.bind("<Configure>", self.on_diamond_frame_configure)
    
    def on_diamond_frame_configure(self,event):
        frame_height = self.diamonds_preview_frame.winfo_height()
    
        if frame_height > 1:
            # if self.controller.get_tab_info()[0] != "general_inventory":
            #     if frame_height == 270:
            #         self.diamonds_preview_frame.configure(width=120,height=120)
            #         self.root.add_hazard_symbols(self.root.stored_diamonds)
            
            self.diamonds_preview_frame.unbind("<Configure>")

    def add_hazard_symbols(self,symbols=[]):
        self.remove_all_children(self.diamonds_preview_frame)
        
        #Exit function if no hazard symbols
        if not symbols: return
        
        min_width = 35  # Set a minimum width for the image
        num_hazard_labels = len(symbols)
       
        #self.diamonds_preview_frame.configure(height=120)
        #print(self.diamonds_preview_frame.winfo_height())
        label_width = max(int(120 * (1/num_hazard_labels)) - 5,min_width)
        label_height = max(int(120 * (1/num_hazard_labels)) - 5,min_width)
        
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
                if symbol in item[0]:
                    # Open the image
                    image = Image.open(item[1])
                    #print(image.size)
                    # Resize the image to the desired dimensions
                    resized_image = image.resize((label_width, label_height), Image.LANCZOS)
                    
                    # Create the CTkImage object with the resized image (SIZE=(LABEL_WIDTH,LABEL_HEIGHT))
                    ctk_image = customtkinter.CTkImage(light_image=resized_image, dark_image=resized_image, size=(label_width,label_height))

                    # Create the CTkLabel with the image
                    hazard_label = customtkinter.CTkLabel(self.diamonds_preview_frame, image=ctk_image, text="")
                    
                    # Add the label to the grid, ensure proper expansion with sticky="nsew"
                    hazard_label.grid(row=row, column=col, sticky="nsew")

                    col += 1

                    # If the column reaches the max number of columns, reset it to 0 and move to the next row
                    if col >= max_cols:
                        col = 0
                        row += 1

            if row >= max_rows:
                break
        
        self.root.stored_diamonds = symbols
    
    def remove_all_children(self,frame):
        for widget in frame.winfo_children():
            widget.destroy()
    
    def switch_preview_box(self):
        #Clear entries from current tab
        self.create_preview_label(self.orientation_option_menu.get(),self.controller.get_tab_info()[0],hazards=True)


class HazardPrecautionFrame2(customtkinter.CTkFrame):
    def __init__(self, parent, controller, warning_dict, root, images=False,hazard_print=None):
        super().__init__(parent)
        self.parent = parent
        self.root = root
        self.hazard_print = hazard_print
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

        # Hazard preview entry
        preview = self.root.area_4
        num_selections = 0
        #Change hazard text box
        if selections is not None:
            for var, label, *rest in selections:
                if var.get():
                    if not label[5:].endswith('.'):
                        text += f"{label[5:]}. "
                    else:
                        text += f"{label[5:]} "
                    num_selections += 1
                #print(text)
            #preview.hazards_preview_textbox.delete("1.0", tk.END)  # Clear the existing text
        #preview..hazards_preview_textbox.insert(tk.END, text)  # Insert the updated text
        
        # Resize text as hazards/precautions are added
        if num_selections >= 3:
            self.font_size = 13 - (num_selections // 2)  # Reduce font size for every 5 selections
            if self.font_size < 6:  # Minimum font size
                self.font_size = 6
            preview.hazard_preview_font_size = self.font_size
            preview.adjust_font_size(preview.hazards_preview_textbox)
        
        #Change diamonds
        diamonds = self.controller.get_diamond_vars()
        diamond_images = []
        if diamonds is not None:
            for var, label, *rest in diamonds:
                if var.get():
                    diamond_images.append(label)
        
        #Finally, update preview box
        preview.update_preview_box([text,diamond_images])

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
                image = customtkinter.CTkImage(
                    dark_image=resized_image,
                    size=(80,80)
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



class DetailSelectFrame(customtkinter.CTkFrame):
    def __init__(self, parent, controller, table,root):
        super().__init__(parent)
        
        self.parent = parent
        self.root = root
        self.controller = controller
        self.entry_strings = {}
        self.table = table


        table_columns_dict = self.controller.get_database_column_names(
            self.root.table_types[''.join(table)]
        )
        
        self.details_checkboxes = {} # Use checkboxes to add/remove from preview
        self.details_string_vars = {}

        #Current tab is accessible from controller class
        if table_columns_dict:
            self.controller.set_tab(''.join(table))
        
        self.update_product_id()

        #Store all EntryBox widgets
        self.entry_vars = {}

        # *Important* - Store entrybox values (when they change)
        #self.area_1_entries = {}

        #Other
        #Refresh product info area
        for widget in self.root.area_1_frames:
            widget.destroy()

        self.root.area_1_frames.append(self)

        # Generate labels and entries for key details area
        self.initialize_tab_dropdown(self.root.table_types)
        max_rows_per_column,row,col,entry_count = self.add_key_details(table_columns_dict)
        self.add_address_entry(row,col,entry_count)
        self.add_to_db_checkbox(max_rows_per_column)

    def initialize_tab_dropdown(self, tables):
        #tab_names = [name if "details" not in name.lower() else "Chemical Details" for name in tables]
        tab_names = list(tables.keys())

        #self.selected_tab = customtkinter.StringVar(value=tab_names[0])

        choose_dropdown = customtkinter.CTkLabel(
            self,
            text="Choose an Inventory Type",
            font=customtkinter.CTkFont(size=14),
        )
        choose_dropdown.grid(row=0, column=0, padx=10, pady=20)
        tab_dropdown = customtkinter.CTkOptionMenu(
            self,
            values=tab_names,
            command=self.dropdown_callback,  
            fg_color=("gray20", "gray40"), 
            button_color=("gray30", "gray50"), 
        )
        tab_dropdown.grid(row=0, column=1, padx=10, pady=20)
        tab_dropdown.set(self.controller.get_tab_name())

        # Store the dropdown in the tab_buttons dictionary
        self.tab_buttons = {name: tab_dropdown for name in tab_names}
    

    def dropdown_callback(self, selected_name):
        # This method will be called when a tab is selected from the dropdown
        self.selected_inventory_type = selected_name
        self.root.switch_tab(selected_name)
    

    def update_product_id(self):
        # Fetch new tab name & latest id from table
        tab_name = self.root.inventory_type.replace(" ","_")
        fetched_id = self.controller.next_id_str(self.controller.next_id(tab_name))

        self.controller.set_id_info(tab_name,fetched_id)

        next_product_id = self.controller.get_id_info()[tab_name]

        self.controller.set_new_barcode(next_product_id)
        self.root.generate_barcode(self.controller.get_new_barcode())
    
    def process_columns(self,column):
        column_lower = column.lower()  # Convert column to lowercase for case-insensitive checks
        
        if "quantity" in column_lower:
            
            words = column_lower.split("_")
            formatted_words = " ".join([word.title() for word in words])
            return formatted_words

        # Handle foreign key columns (those containing 'fk') by removing 'fk' and capitalizing the first word
        elif "fk" in column_lower:
            words = column_lower.split("_")
            words.remove("fk")
            return words[0].title()

        return column.title()

    def unprocess_columns(column):
        column_lower = column.lower()  # Convert column to lowercase for case-insensitive checks

        # If the column starts with a capitalized word that originally had 'quantity'
        if column_lower == column and "quantity" in column_lower:
            return column_lower

        if column_lower != column and "fk" not in column_lower:
            words = column.lower().split("_")
            return "fk_" + "_".join(words)

        # Return the column as is if no changes are necessary
        return column

    #ADD TO DATABASE LABEL
    def add_to_db_checkbox(self,rows):
        self.add_to_db_var = customtkinter.StringVar(value="off")
        self.db_insertion_checkbox = customtkinter.CTkCheckBox(
            self,
            text="Add to database",  # Label for the checkbox
            variable=self.add_to_db_var,  # Bind to the StringVar to track its state
            onvalue="on",  # The value when the checkbox is checked
            offvalue="off",  # The value when the checkbox is unchecked
            command=self.root.checkbox_changed  # Function to call when the state changes
        )
        self.db_insertion_checkbox.grid(row=rows+1, column=0, padx=10, pady=10, sticky="sw")

    def add_key_details(self,table_col):
        max_rows_per_column = 9
        row = 1 
        col = 0
        entry_count = 0
        for i, (key, column_list) in enumerate(table_col.items()):
            if 'product' in ''.join(self.table).lower():
                if 'batch' in key:
                    self.area_1_header = customtkinter.CTkLabel(
                    self,
                    text=key.replace("_"," ").title(),
                    font=customtkinter.CTkFont(size=18, weight="bold"),
                    )
                    self.area_1_header.grid(row=row, column=col, padx=10, pady=10, sticky="w")
                    row += 1
            else:
                #Table headers
                self.area_1_header = customtkinter.CTkLabel(
                self,
                text=key.replace("_"," ").title(),
                font=customtkinter.CTkFont(size=18, weight="bold"),
                )
                self.area_1_header.grid(row=row, column=col, padx=10, pady=10, sticky="w")
                row += 1
            
            # table_label_text = self.label_tables(key, i)
            formatted_table_columns = self.format_names(column_list)
            if "product" in ''.join(self.table).lower():
                if "batch" in key.lower():
                    row = self.add_batch_entries(column_list) + 1
            else:
                for j, column in enumerate(column_list):
                    if "id" in column.lower() or "hazard" in column.lower():
                        continue
                    formatted_table_columns[j] = self.process_columns(column)

                    # Increase row if set to 0
                    if row == 1: row += 1
                    # Create the label for the column
                    # show_on_preview_checkbox = customtkinter.CTkCheckBox(
                    #     self,
                    #     text="",  # Label for the checkbox
                    #     #variable=self.add_to_db_var,  # Bind to the StringVar to track its state
                    #     onvalue="on",  # The value when the checkbox is checked
                    #     offvalue="off",  # The value when the checkbox is unchecked
                    #     #command=self.root.checkbox_changed  # Function to call when the state changes
                    # )
                    # show_on_preview_checkbox.grid(row=row, column=col, padx=10, pady=5, sticky="ew")

                    #var = tk.BooleanVar()
                    var = customtkinter.StringVar(value="off")

                    if 'qr' in column:
                        label = customtkinter.CTkLabel(
                            self, 
                            text=formatted_table_columns[j], 
                        )
                    else:
                        label = customtkinter.CTkCheckBox(
                            self, 
                            text=formatted_table_columns[j], 
                            variable=var, 
                            onvalue="on",  # The value when the checkbox is checked
                            offvalue="off",  # The value when the checkbox is unchecked
                            command=lambda:self.update_details_checkboxes()
                        )
                    label.grid(row=row, column=col, padx=10, pady=5, sticky="ew")
                    # print(formatted_table_columns[j],f"Label Placed Row: {row} | Col: {col}")
                    if row == max_rows_per_column - 1:
                        label.grid(row=row, column=col, padx=10, pady=5)
                    if isinstance(label, customtkinter.CTkCheckBox) and column not in self.details_checkboxes: # Prevent duplicates
                        self.details_checkboxes[column] = label
                        self.details_string_vars[column] = var

                    sv = customtkinter.StringVar()

                    if column not in self.entry_strings.keys():
                        self.entry_strings[column] = (sv)
                    sv.trace("w", lambda *args, name=column, index=entry_count: self.update_key_details(name,index))
                    

                    # Create the entry for the column
                    entry = customtkinter.CTkEntry(self,textvariable=sv)
                    entry.bind("<Return>", lambda event, name=column, index=entry_count: self.on_enter_pressed(name, index))

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
                    if column not in self.entry_vars.keys():
                        self.entry_vars[column] = entry

                    row += 1
                    entry_count += 1
                    if row >= max_rows_per_column:
                        row = 1
                        col += 2 
        return [max_rows_per_column,row,col,entry_count]
    
    def add_address_entry(self,row,col,entry_count):
        #Address Entry
        address_label = customtkinter.CTkLabel(
            self, text="Address:"
        )
        address_label.grid(row=row, column=col, padx=10, pady=5, sticky="ew")

        sv2 = customtkinter.StringVar()

        self.entry_strings["address"] = (sv2)
        sv2.trace("w", lambda *args, name="address", index=entry_count: self.update_key_details(name,index))

        address_entry = customtkinter.CTkEntry(self,textvariable=sv2)
        address_entry.bind("<Return>", lambda event, name="address", index=entry_count: self.on_enter_pressed(name, index))
        address_entry.grid(row=row, column=col+1, padx=10, pady=5, sticky="w")

        # Add address string
        self.entry_vars["address"] = address_entry
    
    def add_batch_entries(self,table):
        max_rows_per_column = 7
        row = 2 
        col = 0
        entry_count = 0
        formatted_table_columns = self.format_names(table)
        for j, column in enumerate(table):
            if "id" in column.lower() or "hazard" in column.lower():
                continue
            formatted_table_columns[j] = self.process_columns(column)
            
            var = customtkinter.StringVar(value="off")
            # Create the label for the column
            label = customtkinter.CTkCheckBox(
                self, 
                text=formatted_table_columns[j], 
                variable=var, 
                onvalue="on",  # The value when the checkbox is checked
                offvalue="off",  # The value when the checkbox is unchecked
                command=lambda:self.update_details_checkboxes()
            )
            label.grid(row=row, column=col, padx=10, pady=5, sticky="ew")
            #print(formatted_table_columns[j],f"Label Placed Row: {row} | Col: {col}")
            if row == max_rows_per_column - 1:
                label.grid(row=row, column=col, padx=20, pady=5)
            if isinstance(label, customtkinter.CTkCheckBox) and column not in self.details_checkboxes: # Prevent duplicates
                self.details_checkboxes[column] = label
                self.details_string_vars[column] = var
            sv = customtkinter.StringVar()

            self.entry_strings[column] = (sv)
            sv.trace("w", lambda *args, name=column, index=entry_count: self.update_key_details(name,index))


            # Create the entry for the column
            entry = customtkinter.CTkEntry(self,textvariable=sv)
            entry.bind("<Return>", lambda event, name=column, index=entry_count: self.on_enter_pressed(name, index))
            
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
        
        #self.extra_batch_columns(row,col)
        return row

        
    
    def extra_batch_columns(self,rows,cols):
        self.inventory = self.controller.get_chemical_inventory_stock()
        
        # Create and place the dropdown (CTkOptionMenu) widget
        self.dropdown = customtkinter.CTkOptionMenu(
            self,
            values=self.inventory, 
            fg_color=("gray20", "gray40"), 
            button_color=("gray30", "gray50"), 
            width=200
        )
        
        self.dropdown.grid(row=rows+2, column=cols,padx=10, pady=5)
        self.dropdown.set("Choose Chemical(s) from Inventory")

    def update_key_details(self, *args):

        #Load StringVar object
        entry_name = args[0]

        str_var = self.entry_strings[entry_name]
        
        if 'address' in entry_name:
            if not str_var.get():
                self.entry_strings[entry_name] = self.root.default_address
        #self.area_1_entries[entry_name] = str_var.get()
        
        # Do something with the updated value (for now, just print it)
        #print(f"Entry {entry_name} updated: {str_var.get()}")

        tab_names = self.controller.get_tab_info()
        entries = self.controller.get_data_entries()
        
        #Set preview text labels
        self.update_preview_labels(entry_name,str_var.get(),self.root.preview_key_details)
    
    
    def update_preview_labels(self,entry,value,preview_labels):
        for key in preview_labels.keys():
            if entry in key:
                preview_name = self.root.format_names(entry)
                new_entry =  f"{preview_name}: {value}"
                #print(f"Insert: {key} | Value: {entry}")
               
                if "address" in entry:
                    if not value:
                        default_address = str(f"{self.root.default_address}")
                        preview_labels[key].configure(text=default_address)
                    else:
                        preview_labels[key].configure(text=value)
                else:
                    preview_labels[key].configure(text=new_entry)
    
    
    def on_enter_pressed(self,name, *args):
        
        #Load StringVar object
        entry_name = name
        self.update_entries(True)
        self.update_details_checkboxes()
        
    def update_details_checkboxes(self):
        checked = []
        for key, val in self.details_string_vars.items():
            if val.get() == "on":
                if key in self.details_checkboxes:
                    checked.append(key)
       
        preview = self.root.area_4
        details_textbox = preview.details_preview_textbox
        text = ""
        num_items = 0
        for item in checked:
            if item in self.entry_strings:
                entry_name = item.replace("_"," ").title()
                entry_value = self.entry_strings[item].get()
                text += f"{entry_name}: {entry_value}\n"
                num_items += 1

        if num_items >= 2:
            self.font_size = 13 - (num_items // 2) - 2  # Reduce font size for every 2 selections
            if self.font_size < 6:  # Minimum font size
                self.font_size = 6
            preview.details_preview_font_size = self.font_size
            details_textbox.cget("font").configure(size=preview.details_preview_font_size)
            details_textbox.configure(font=details_textbox.cget("font"))
            #preview.adjust_font_size(preview.details_preview_textbox)
        else:
            preview.details_preview_font_size = 13
            details_textbox.cget("font").configure(size=preview.details_preview_font_size)
            details_textbox.configure(font=details_textbox.cget("font"))
        
        preview.details_preview_textbox.delete("1.0", tk.END)  # Clear the existing text
        preview.details_preview_textbox.insert(tk.END, text)  # Insert the updated text
    
    def disable_details_checkboxes(self):
        for key, val in self.details_string_vars.items():
            # Set each checkbox value to "off"
            val.set("off")
    
    def update_entries(self,send_message):
        str_var = self.entry_strings

        #Check tables for tab - ex: Chemical inventory - [chemical_inventory,geneeral_inventory]
        tab_names = self.controller.get_tab_info()
        data_entered = False
        try:
            for tab in tab_names:
                if 'batch' in tab_names[0]: #Skip synthesis, washing, etc
                    batch = tab_names[0]
                    tab_names = []
                    tab_names.append(batch)
                    if 'batch' not in tab: continue
                for key in str_var:
                    unformatted_column_name = self.undo_format(key)
                    in_table = self.controller.check_column_exists(tab,unformatted_column_name,str_var[key].get())
                    if in_table:
                        data_set = self.controller.set_data_entries(unformatted_column_name,str_var[key].get(),tab_names)
                        if "qr" in unformatted_column_name:
                            self.controller.set_qr_code_entry(str_var[key].get())
                        else: data_entered = True
                
            
            data_entered = self.check_for_empty(data_set)

            if send_message:
                if not data_entered[0]: self.root.data_process_message(f"Updated Entries Successfully")
                else: self.root.data_warning_message(f"No values inserted for {data_entered[1]}")
            #print(self.controller.get_data_entries())
            
        except KeyError as e:
            self.root.data_error_message(f"Failed to Update Entries: \n\nKeyError: {e}")
        except Exception as e:
            self.root.data_error_message(f"Failed to Update Entries: An error occurred: \n\n{e}")
    
    def check_for_empty(self,set):
        for key in set.keys():
            if set[key]:
                all_none = all(value is None for value in set[key].values())
                if all_none:
                    print(f"No entries for {key} table")
                    return (True,key)
        return (False, None)

    # Ex: chemical_inventory -> Chemical Inventory
    def format_names(self, names):
        if type(names) is list:
            return [name.replace("_", " ").title() for name in names]
        elif type(names) is str:
            return names.replace("_", " ").title()
    
    def undo_format(self, name):
        # Revert the title case and replace spaces with underscores
        return name.lower().replace(" ", "_")


class WarningSelectFrame(customtkinter.CTkFrame):
    def __init__(self, parent, controller, hazards,precautions, root):
        super().__init__(parent)

        self.root = root
        self.parent = parent
        self.controller = controller

        # Make columns expandable
        for col in range(4):
            self.grid_columnconfigure(col, weight=1)

        # Create hazard frame
        self.create_header(self, "Hazard Details", 0)
        self.hazard_frame = self.create_frame(self, hazards, 1)  # Add appropriate hazard_print value

        # Create precautionary frame
        self.create_header(self, "Precautionary Details", 2)
        self.precautions_frame = self.create_frame(self, precautions, 3)


    # Helper function to create header labels
    def create_header(self, parent, text, row):
        header = customtkinter.CTkLabel(
            parent,
            text=text,
            font=customtkinter.CTkFont(size=18, weight="bold"),
        )
        header.grid(row=row, column=0, padx=10, pady=10, sticky="w")
        return header

    # Helper function to create frames
    def create_frame(self, parent, warning_dict, row, hazard_print=None):
        frame = HazardPrecautionFrame2(
            parent,
            controller=self.controller,
            warning_dict=warning_dict,
            root=self.root,
            images=False,
            hazard_print=hazard_print
        )
        frame.grid(row=row, column=0, columnspan=4, padx=10, pady=10, sticky="ew")
        frame.grid_columnconfigure(4, weight=1)
        return frame

class WarningPrintFrame(customtkinter.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        # Configure columns
        for col in range(4): self.grid_columnconfigure(col, weight=1)

        # Create header and textbox
        self.area_5_header = customtkinter.CTkLabel(self, text="Print", font=customtkinter.CTkFont(size=18, weight="bold"))
        self.area_5_header.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.text_box = customtkinter.CTkTextbox(self, height=100)
        self.text_box.grid(row=1, column=0, columnspan=2, padx=10, pady=(5, 10))


class HazardSymbolFrame(customtkinter.CTkFrame):
    def __init__(self, parent, controller, diamonds, root, hazard_print=None):
        super().__init__(parent)    
        
        self.root = root
        self.parent = parent
        for col in range(4):  # Configure first 4 columns with weight=1
            self.grid_columnconfigure(col, weight=1)

        self.area_3_header = customtkinter.CTkLabel(
            self,
            text="Hazard Symbols",
            font=customtkinter.CTkFont(size=18, weight="bold"),
        )
        self.area_3_header.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.hazard_diamonds_frame = HazardPrecautionFrame2(
            self,
            controller,
            warning_dict=diamonds,
            root=self.root,
            images=True,
            hazard_print=hazard_print,
        )
        self.hazard_diamonds_frame.grid(
            row=1, column=0, columnspan=4, padx=10, pady=10, sticky="ew"
        )

        self.hazard_diamonds_frame.grid_columnconfigure(4, weight=1)