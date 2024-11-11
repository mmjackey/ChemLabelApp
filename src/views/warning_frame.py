import tkinter as tk
from tkinter import ttk

from PIL import Image, ImageTk


class HazardPrecautionFrame(tk.Frame):
    def __init__(self, parent, controller, warning_dict, images=False):
        super().__init__(parent)

        first_key = list(warning_dict.keys())[0]

        self.controller = controller

        # Signal Word selection
        self.warning_type_var = tk.StringVar(value=first_key)  # Default value

        self.warning_type_menu = tk.OptionMenu(
            self, self.warning_type_var, *warning_dict.keys()
        )

        self.warning_type_menu.grid(row=0, column=1, padx=10, pady=5)

        self.warning_type = None

        if "hazard" in first_key.lower():
            self.warning_type = "Hazard"
        elif "precautionary" in first_key.lower():
            self.warning_type = "Precaution"
        elif "diamond" in first_key.lower():
            self.warning_type = "Diamond"

        self.select_warning_label = ttk.Label(
            self, text=f"Select {self.warning_type} Type:"
        )
        self.select_warning_label.grid(row=0, column=0, padx=10, pady=5)

        #  Textbox for selected warning details
        self.text_box = tk.Text(self, height=5, width=40)
        self.text_box.grid(row=1, column=0, columnspan=2, padx=10, pady=5)

        self.warning_type_frames = {}

        for i, warning_type in enumerate(list(warning_dict.keys())):
            if i == 0:
                frame = WarningClassCheckboxes(
                    self,
                    warning_dict[warning_type],
                    default_class=True,
                    images=images,
                )
            else:
                frame = WarningClassCheckboxes(
                    self, warning_dict[warning_type], images=images
                )
            self.warning_type_frames[warning_type] = frame

        self.warning_type_var.trace_add(
            "write",
            lambda *args: self.switch_frame(),
        )

    def switch_frame(self):
        frame = self.warning_type_var.get()
        self.hide_frames()
        self.show_frame(self.warning_type_frames[frame])

    def show_frame(self, frame):
        frame.grid(row=2, column=0, columnspan=2, padx=10, pady=5)

    def hide_frames(self):
        for frame in self.warning_type_frames.values():
            frame.grid_forget()

    def update_text_box(self):
        text = ""
        if self.warning_type == "Hazard":
            warning_vars = self.controller.get_selected_hazards()
        elif self.warning_type == "Precaution":
            warning_vars = self.controller.get_selected_precautions()
        elif self.warning_type == "Diamond":
            warning_vars = self.controller.get_diamond_vars()

        if warning_vars is not None:
            for var, label, *rest in warning_vars:
                if var.get():
                    text += f"{label}\n"
            self.text_box.delete("1.0", tk.END)  # Clear the existing text
            self.text_box.insert(tk.END, text)  # Insert the updated text


class WarningClassCheckboxes(tk.Frame):
    def __init__(
        self, parent, warning_items, default_class=False, images=False
    ):
        super().__init__(parent)
        self.parent = parent
        self.warning_items = warning_items

        self.generate_checkboxes(images=images)

        if default_class:
            self.grid(row=2, column=0, columnspan=2, padx=10, pady=5)

    def generate_checkboxes(self, images=False):
        self.checkboxes_frame = tk.Frame(self)
        self.checkboxes_frame.grid(row=0, column=0)

        for item in self.warning_items:
            if images:
                image = Image.open(item[1])
                resized_image = image.resize((100, 100), Image.LANCZOS)
                image = ImageTk.PhotoImage(resized_image)
                item = item[0]
            else:
                image = None
            var = tk.BooleanVar()
            checkbox = ttk.Checkbutton(
                self.checkboxes_frame,
                text=item,
                image=image,
                compound="left",
                variable=var,
                command=lambda var=var: self.parent.update_text_box(),
            )
            checkbox.image = image

            checkbox.pack(anchor="w", fill="x")
            # Keep track of checkbox vars and labels
            if self.parent.warning_type == "Hazard":
                self.parent.controller.append_hazard_variables(var, item)
            elif self.parent.warning_type == "Precaution":
                self.parent.controller.append_precautions_variables(var, item)
            elif self.parent.warning_type == "Diamond":
                self.parent.controller.append_diamond_variables(
                    var, item, image
                )
