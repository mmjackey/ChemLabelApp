import customtkinter
import tkinter as tk
from tkinter import ttk

from PIL import Image, ImageTk


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

        #Change hazard text box
        if selections is not None:
            for var, label, *rest in selections:
                if var.get():
                    text += f"{label}\n"
            self.hazard_print.delete("1.0", tk.END)  # Clear the existing text
        self.hazard_print.insert(tk.END, text)  # Insert the updated text

        #Change diamonds
        diamonds = self.controller.get_diamond_vars()
        diamond_images = []
        if diamonds is not None:
            for var, label, *rest in diamonds:
                if var.get():
                    diamond_images.append(label)
        
        #Finally, update preview box
        self.root.update_preview_box([text,diamond_images])

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