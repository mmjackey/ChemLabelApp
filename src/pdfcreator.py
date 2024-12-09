import customtkinter as ctk
import tkinter as tk
from tkinter import Tk, filedialog, messagebox, ttk
from tkinter import Toplevel
from PIL import Image, ImageTk, ImageGrab
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from views.CTkXYFrame import *
from views.CTkMessagebox import *
from views.widgets import *
import os
from math import ceil
from reportlab.lib.pagesizes import letter

class PDFCreator(ctk.CTkFrame):
    def __init__(self,parent,frame,widgets,root):
        super().__init__(parent)
        self.configure(width=1050,height=630,corner_radius=0)
        self.save_pdf_callback = None
        self.parent = parent
        self.frame = frame
        self.widgets = widgets
        self.root = root
        self.detail_entries = self.root.area_1.entry_strings

        self.print_count = 0 # Keep track of label pdf names

    def load_options(self):
        # Available label sizes (for chemical label)
        self.label_sizes = {
            "105 x 74 mm": (105, 74),
            "105 x 148 mm": (105, 148),
            "52 x 74 mm": (52, 74),
            "99 x 57 mm": (99, 57)
        }

        # Create the dropdown menu with the label sizes
        

        self.print_header = ctk.CTkLabel(
            self,
            text="Print & Preview",
            font=ctk.CTkFont(size=18, weight="bold"),
        )
        self.print_header.grid(row=0, column=0, columnspan=3, sticky="w", padx=10, pady=10)

        
        
        # Label to explain what the dropdown is for
        self.label_info = ctk.CTkLabel(self, text="Choose Label Size:")
        self.label_info.grid(row=1, column=0, sticky="w", padx=10, pady=10)


        self.label_size_dropdown = ctk.CTkOptionMenu(
            master=self, 
            values=list(self.label_sizes.keys()), 
            command=self.on_label_size_select,
            fg_color=("gray20", "gray40"), 
            button_color=("gray30", "gray50"), )
        self.label_size_dropdown.grid(row=1, column=1, sticky="w", padx=10, pady=10)

        self.label_info2 = ctk.CTkLabel(self, text="(8 per sheet)")
        self.label_info2.grid(row=2, column=1, sticky="w", padx=10, pady=10)


        self.submit_button = ctk.CTkButton(
            self, 
            text="Submit (Final)",   # Button text
            command=self.on_button_click,  # Function to call on click
            fg_color=("gray20", "gray40"),   # Make the button transparent
        )
        self.submit_button.grid(row=1, column=2, sticky="w",padx=10, pady=10)

        self.label_window = customtkinter.CTkFrame(
                    self,
                    fg_color="#FAF9F6", 
                    corner_radius=0
        )  # Create a frame to hold the generated label
        self.label_window.grid(row=2, column=2, sticky="w", padx=10, pady=10)
        initial_width = self.mm_to_pixels(105)
        initial_height = self.mm_to_pixels(74)
        self.label_window.configure(width = initial_width, height= initial_height)
        self.label_window.grid_propagate(False)
        self.label_window.bind("<Button-1>", self.on_click)
        for col in range(4):
            weight = 1 if col < 3 else 0
            self.label_window.grid_columnconfigure(col, weight=weight)
        self.label_window.grid_rowconfigure(1, weight=0)
        self.label_window.grid_columnconfigure(2, weight=1)  # Empty column for spacing
        self.label_window.grid_rowconfigure(4,weight=1)

        close_button = customtkinter.CTkButton(
            self,
            text="Close", 
            command=self.root.close_popup,
            border_width=0, 
            fg_color="transparent")
        close_button.place(relx=1.0, rely=0.0, anchor="ne", relheight=0.05, relwidth=0.2, x=-10, y=10)

        #Start w default
        self.on_label_size_select("105 x 74 mm")

        

    def on_button_click(self):
        # This will be called when the button is clicked
        self.save_to_pdf(self.label_window)

    def on_label_size_select(self,selected_size):
        index = 0
        for item in self.label_sizes.keys():
            index += 1
            if selected_size in item:
                match index:
                    case 1: 
                        self.label_info2.configure(text="(8 per sheet)")
                        self.sheet_count = 8
                    case 2: 
                        self.label_info2.configure(text="(4 per sheet)")
                        self.sheet_count = 4
                    case 3: 
                        self.label_info2.configure(text="(16 per sheet)")
                        self.sheet_count = 16
                    case 4: 
                        self.label_info2.configure(text="(10 per sheet)")
                        self.sheet_count = 10
        self.create_label(self.label_sizes[selected_size])
    
    def create_label(self,label_size):
        mm_width = int(label_size[0])
        mm_height = int(label_size[1])
        dpi = 96  # Assuming a screen DPI of 96
        scale = 1
        self.base_width = 396
        self.base_height = 279
        #print(f"mm ({mm_width},{mm_height})")
        width_px = self.mm_to_pixels(mm_width, dpi, scale)
        height_px = self.mm_to_pixels(mm_height, dpi, scale)

        self.scaling_factor = self.calculate_scaling_factor(width_px, height_px,image=True,text=False)
        t_scaling_factor = self.calculate_scaling_factor(width_px, height_px,image=False,text=True)


        print(f"Creating print screen preview: ({mm_width}mm,{mm_height}mm) | ({width_px}px,{height_px}px)")
        self.label_window.configure(width=width_px, height=height_px)

        # Destroy all child widgets first
        self.clear_preview_key_details()

        # Add top images
        self.logo_label = self.create_image_label(AppConfig.LOGO_PREVIEW, (160 * self.scaling_factor, 40 *self.scaling_factor), row=0, column=0, padx = 5, pady = (0,10), sticky="w")
        self.barcode_label_prev = self.create_image_label("barcode.png", (60 * self.scaling_factor, 60 * self.scaling_factor), row=0, column=1, padx=0, sticky="e")
        self.qr_code_label = self.create_image_label(
            "resources/images/qr_code.png", 
            (80 * self.scaling_factor, 80 * self.scaling_factor), 
            row=0, 
            column=2, 
            padx=(0, 5),
            sticky="e"
        )

        # Recreate key details preview textbox
        self.d_textbox = customtkinter.CTkTextbox(
            self.label_window, 
            height=100 * t_scaling_factor, 
            width=275 * self.scaling_factor, 
            fg_color="transparent", 
            text_color="black", 
            wrap="word",
        )
        self.d_textbox.grid(row=3, column=0, columnspan=1, padx=2, sticky="ew")

        text=""
        if self.root.preview_key_details:
            for entry in self.detail_entries.keys():
                if 'qr' in entry: continue
                if self.detail_entries[entry].get():
                    value = self.detail_entries[entry].get()
                    preview_name = self.root.format_names(entry)
                    text +=  f"{preview_name}: {value}\n"
                    #print(text)
            self.d_textbox.delete("1.0", tk.END)
            self.d_textbox.insert(tk.END, text)

            d_t_font = self.d_textbox.cget("font")
            d_num_selections = len(text.split("\n"))
            if d_num_selections >= 2:
                d_scaled_font_size = int((13 - (d_num_selections // 2) - 2) * self.scaling_factor)  # Reduce font size for every 5 selections
                if d_t_font._size < 4:  # Minimum font size
                    d_scaled_font_size = 4
                d_t_font.configure(size=d_scaled_font_size)
                self.d_textbox.configure(font=d_t_font)
                print(f"(Print Screen Details Box) New Font Size: {d_scaled_font_size}")



        # Recreate Hazards preview
        self.h_textbox = customtkinter.CTkTextbox(
            self.label_window,
            height=110 * t_scaling_factor, 
            width=275 * self.scaling_factor, 
            fg_color="transparent", 
            text_color="black", 
            wrap="word",
        )
        self.h_textbox.grid(row=4, column=0, columnspan=1, padx=2, sticky="ew")
        if self.root.stored_preview_text:
            self.h_textbox.delete("1.0", tk.END)
            self.h_textbox.insert(tk.END, self.root.stored_preview_text)

            h_t_font = self.h_textbox.cget("font")
            num_selections = len(self.root.stored_preview_text.split(".")) - 1
            if num_selections >= 3:
                h_scaled_font_size = int((13 - (num_selections // 2)) * self.scaling_factor)  # Reduce font size for every 5 selections
                if h_t_font._size < 4:  # Minimum font size
                    h_scaled_font_size = 4
                h_t_font.configure(size=h_scaled_font_size)
                self.h_textbox.configure(font=h_t_font)
                print(f"(Print Screen Hazards Box) New Font Size: {h_scaled_font_size}")
        
        
        
        # Address
        self.address_label = customtkinter.CTkLabel(
            self.label_window, 
            text=self.root.default_address, 
            text_color="black", anchor="w", 
            wraplength=300, 
            fg_color="transparent"
        )
        self.address_label.grid(row=5, column=0, columnspan=1, padx=2, pady=(0,self.scaling_factor), sticky="ew")

        #Resizing address label text
        address_font = self.address_label.cget("font")
        scaled_font_size = int(address_font._size * self.scaling_factor)
        address_font.configure(size=scaled_font_size)
        self.address_label.configure(font=address_font)

        if 'address' in self.root.preview_key_details and 'address' in self.detail_entries:
            address_value = self.detail_entries['address'].get()
            if address_value:
                print(address_value)
                self.address_label.configure(text=address_value)

        self.label_window.grid_columnconfigure(1, weight=1)  # Configure column 1 to expand if necessary
        self.label_window.grid_columnconfigure(2, weight=1)
        # Create the label with the chosen size
        #label = ctk.CTkLabel(self.label_window, text=f"Chemical Label ({label_size})", font=("Arial", label_size))
        #label.pack(pady=50)
        
        self.test_label = ctk.CTkFrame(self.label_window, width=140 * self.scaling_factor, height=140 * self.scaling_factor, fg_color="transparent")
        self.place_hazard_symbols()
    
    def create_image_label(self, image_path, size, row, column, sticky, padx=(0, 0), pady=(0,0)):
        image = Image.open(image_path)
        image_preview = customtkinter.CTkImage(dark_image=image, size=size)
        label = customtkinter.CTkLabel(self.label_window, image=image_preview, text="")
        label.grid(row=row, column=column, padx=padx, pady=pady, sticky=sticky)
        return label

    def clear_preview_key_details(self):
        for widget in self.label_window.winfo_children():
            widget.destroy()
        
    def calculate_scaling_factor(self, new_width, new_height,image=False,text=False):
        # Scaling factor starts at 1 (no scaling)
        scaling_factor = 1

        # Compare the new size with the base size and calculate the scaling factor
        if text:
            if new_width > self.base_width or new_height > self.base_height:
                # Increase the scaling factor if the new size is larger
                scaling_factor = max(new_width / self.base_width, new_height / self.base_height)
        if text or image:
            if new_width < self.base_width or new_height < self.base_height:
                # Decrease the scaling factor if the new size is smaller
                scaling_factor = min(new_width / self.base_width, new_height / self.base_height)

        return scaling_factor

    def mm_to_pixels(self,mm, dpi=96, scale=1):
        return int(mm * dpi / 25.4  * scale)

    def on_click(self,event):
        # event.x and event.y are the coordinates of the click relative to the frame
        print(f"Clicked at x: {event.x}, y: {event.y}")
        width = self.label_window.cget("width")
        height = self.label_window.cget("height")

        label_width = self.test_label.cget("width")
        label_height = self.test_label.cget("height")

        x = width - label_width - (10 * self.scaling_factor)
        y = height - label_height - (10 * self.scaling_factor)
        
        self.test_label.place(x=x, y=y)
    
    def place_hazard_symbols(self):
        width = self.label_window.cget("width")
        height = self.label_window.cget("height")

        label_width = self.test_label.cget("width")
        label_height = self.test_label.cget("height")

        x = width - label_width - (10 * self.scaling_factor)
        y = height - label_height - (10 * self.scaling_factor)
        
        self.test_label.place(x=x, y=y)

        self.diamond_example = ctk.CTkLabel(
            self.test_label,
            width=label_width/4,
            height=label_width/4,
            fg_color="white",
            text=""
        )
        self.diamond_example.place(relx=0.5,rely=0.5,anchor="center")

        self.diamond_mappings = {
            "1": [(0.5,0.5)],
            "2": [(0.3, 0.5), (0.7, 0.5)],
            "3": [(0.25, 0.5), (0.5, 0.5), (0.75, 0.5)],
            "4": [(0.5, 0.2), (0.5, 0.8), (0.2, 0.5), (0.8, 0.5)],
            "5": [(0.25, 0.25), (0.5, 0.25), (0.75, 0.25), (0.25, 0.5), (0.5, 0.5), (0.75, 0.5)],  # 3x3 Grid (first 6 positions)
            "6": [(0.25, 0.25), (0.5, 0.25), (0.75, 0.25), (0.25, 0.5), (0.5, 0.5), (0.75, 0.5), (0.25, 0.75), (0.5, 0.75), (0.75, 0.75)],  # 3x3 Grid (full 9 positions)
            "7": [(0.25, 0.25), (0.5, 0.25), (0.75, 0.25), (0.25, 0.5), (0.5, 0.5), (0.75, 0.5), (0.25, 0.75), (0.5, 0.75), (0.75, 0.75)],  # 3x3 Grid (same as "6")
            "8": [(0.25, 0.25), (0.5, 0.25), (0.75, 0.25), (0.25, 0.5), (0.5, 0.5), (0.75, 0.5), (0.25, 0.75), (0.5, 0.75), (0.75, 0.75)],  # 3x3 Grid (same as "6")
            "9": [(0.25, 0.25), (0.5, 0.25), (0.75, 0.25), (0.25, 0.5), (0.5, 0.5), (0.75, 0.5), (0.25, 0.75), (0.5, 0.75), (0.75, 0.75)]   # 3x3 Grid (same as "6")
        }

        diamonds = self.root.stored_diamonds
        if diamonds:
            self.add_diamond_symbols(diamonds,label_width/1.25)
    
    def add_diamond_symbols(self, symbols,dia_width):
        if not symbols: return
        num_hazard_labels = len(symbols)
        num_hazard_string = str(num_hazard_labels)

        placements = self.diamond_mappings[num_hazard_string]
        #print(placements)

        min_width = int(35 * self.scaling_factor)
        symbol_width = max(int(dia_width * (1/num_hazard_labels)),min_width)
        symbol_height = max(int(dia_width * (1/num_hazard_labels)),min_width)

        #symbol_width = int(symbol_width * self.scaling_factor)
        #symbol_height = int(symbol_height * self.scaling_factor)

        print(symbol_width)
        diamonds_dict = self.root.controller.get_hazard_diamonds_dict()['Diamonds']
        self.added_symbols = []
        for item in diamonds_dict:
            for i,symbol in enumerate(symbols):
                #print(f"Does {item[0]} | equal | {symbol}?")
                if symbol in item[0]:
                    # Open the image
                    image = Image.open(item[1])
                    #print(image.size)
                    # Resize the image to the desired dimensions
                    resized_image = image.resize((symbol_width, symbol_height), Image.LANCZOS)
                    
                    # Create the CTkImage object with the resized image (SIZE=(LABEL_WIDTH,LABEL_HEIGHT))
                    ctk_image = customtkinter.CTkImage(light_image=resized_image, dark_image=resized_image, size=(symbol_width,symbol_height))

                    # Create the CTkLabel with the image
                    hazard_label = customtkinter.CTkLabel(self.test_label, image=ctk_image, text="")
                    self.added_symbols.append(hazard_label)
                    #print(f"Created hazard symbol {i+1}")
        
        for label, placement in zip(self.added_symbols, placements):
            relx, rely = placement
            #print(f"({relx},{rely})")
            label.place(relx=relx, rely=rely, anchor="center")

    def save_to_pdf(self,frame):

        match self.sheet_count:
            case 8: self.sheet_grid = (2,4)
            case 4: self.sheet_grid = (2,2)
            case 16: self.sheet_grid = (4,4)
            case 8: self.sheet_grid = (2,5)

        tmp_png = "preview_frame_output.png"
        self.capture_widget_as_image(frame, tmp_png)
        self.create_pdf_letter(tmp_png, self.sheet_count, self.sheet_grid,f"label{self.print_count}_letter.pdf")
        self.create_pdf_a4(tmp_png, self.sheet_count, self.sheet_grid,f"label{self.print_count}_a4.pdf")
        self.print_count += 1
        #os.remove(tmp_png)
    
    def capture_widget_as_image(self,widget, filename="widget_capture.png"):
        # Get the widget's bounding box
        x = widget.winfo_rootx()
        y = widget.winfo_rooty()
        width = widget.winfo_width()
        height = widget.winfo_height()

        img = ImageGrab.grab(bbox=(x, y, (x + width), (y + height)))
        new_image = img.rotate(-90)
        new_image = img.convert("RGB")
        

        new_image.save(filename)
        print("tmp png created")
    
    def create_pdf_letter(self,image_path, sheet_count, sheet_grid, pdf_filename="output.pdf"):
        page_width, page_height = letter

        c = canvas.Canvas(pdf_filename, pagesize=(page_width, page_height))

        img = Image.open(image_path)
        
        img_width, img_height = img.size

        padding_x = 20
        padding_y = 20

        available_width = page_width - (sheet_grid[0] + 1) * padding_x  # Padding between columns
        available_height = page_height - (sheet_grid[1] + 1) * padding_y  # Padding between rows

        max_image_width = available_width / sheet_grid[0]
        max_image_height = available_height / sheet_grid[1]

        scale_factor = min(max_image_width / img_width, max_image_height / img_height)

        new_width = img_width * scale_factor
        new_height = img_height * scale_factor

        grid_width = (new_width + padding_x) * sheet_grid[0] + padding_x
        grid_height = (new_height + padding_y) * sheet_grid[1] + padding_y

        x_offset_start = (page_width - grid_width) / 2
        y_offset_start = (page_height - grid_height) / 2

        for i in range(sheet_count):
            row = i // sheet_grid[0]
            col = i % sheet_grid[0]

            x_offset = x_offset_start + col * (new_width + padding_x) + padding_x
            y_offset = y_offset_start + (sheet_grid[1] - 1 - row) * (new_height + padding_y) + padding_y
            
            c.drawImage(image_path, x_offset, y_offset, width=new_width, height=new_height)

        c.save()
                    
    def create_pdf_a4(self, image_path, sheet_count, sheet_grid, pdf_filename="output.pdf"):
        # A4 Landscape page size (841.890 x 595.276 points)
        page_width, page_height = landscape(A4)
        
        c = canvas.Canvas(pdf_filename, pagesize=(page_width, page_height))

        img = Image.open(image_path)
        
        img_width, img_height = img.size

        padding_x = 20
        padding_y = 20

        available_width = page_width - (sheet_grid[1] + 1) * padding_x  # Padding between columns
        available_height = page_height - (sheet_grid[0] + 1) * padding_y  # Padding between rows

        max_image_width = available_width / sheet_grid[1]
        max_image_height = available_height / sheet_grid[0]

        scale_factor = min(max_image_width / img_width, max_image_height / img_height)

        new_width = img_width * scale_factor
        new_height = img_height * scale_factor

        grid_width = (new_width + padding_x) * sheet_grid[1] + padding_x
        grid_height = (new_height + padding_y) * sheet_grid[0] + padding_y

        x_offset_start = (page_width - grid_width) / 2
        y_offset_start = (page_height - grid_height) / 2

        for i in range(sheet_count):
            row = i // sheet_grid[1]
            col = i % sheet_grid[1]

            x_offset = x_offset_start + col * (new_width + padding_x) + padding_x
            y_offset = y_offset_start + (sheet_grid[1] - 1 - row) * (new_height + padding_y) + padding_y
            
            c.drawImage(image_path, x_offset, y_offset, width=new_width, height=new_height)

        c.save()