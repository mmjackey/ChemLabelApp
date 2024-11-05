import tkinter as tk

import theme


class Hazard_frame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        # Second tab for Hazard Details
        parent.notebook.add(self, text="Hazard Details")

        self.get_hazards_callback = None
        self.get_selected_hazards_callback = None
        self.append_selected_hazard_callback = None

        self.checkbox_frames_generated = False

        # Signal Word selection
        self.hazard_type_var = tk.StringVar(
            value="Physical Hazards (H2)"
        )  # Default value

        # Function to update checkboxes when hazard type changes
        self.hazard_type_var.trace_add(
            "write",
            lambda *args: self.switch_frame(),
        )

        self.hazard_type_menu = tk.OptionMenu(
            self,
            self.hazard_type_var,
            "Physical Hazards (H2)",
            "Health Hazards (H3)",
            "Environmental Hazards (H4)",
        )
        self.hazard_type_menu.config(
            bg=theme.BUTTON_COLOR,
            fg=theme.TEXT_COLOR,
            activebackground=theme.HIGHLIGHT_COLOR,
        )

        self.select_hazard_label = tk.Label(
            self,
            text="Select Hazard Type:",
            bg=theme.BACKGROUND_COLOR,
            fg=theme.TEXT_COLOR,
        )
        self.select_hazard_label.grid(row=0, column=0, padx=10, pady=5)

        self.hazard_type_menu.grid(row=0, column=1, padx=10, pady=5)

        #  Textbox for hazard details
        self.text_box = tk.Text(
            self,
            height=5,
            width=40,
            bg=theme.ENTRY_COLOR,
            fg=theme.TEXT_COLOR,
            insertbackground=theme.TEXT_COLOR,
        )
        self.text_box.grid(row=1, column=0, columnspan=2, padx=10, pady=5)

        # Container for hazard checkboxes
        self.checkboxes_container = tk.Frame(self, bg=theme.BACKGROUND_COLOR)
        self.checkboxes_container.grid(
            row=2, column=0, columnspan=2, padx=10, pady=5, sticky="nsew"
        )

        # Configure grid weights
        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        self.checkboxes_container.rowconfigure(0, weight=1)
        self.checkboxes_container.columnconfigure(0, weight=1)

        self.h2_checkboxes_frame = HazardClassCheckboxes(
            self, default_class=True
        )
        self.h3_checkboxes_frame = HazardClassCheckboxes(self)
        self.h4_checkboxes_frame = HazardClassCheckboxes(self)

    def switch_frame(self):
        match self.hazard_type_var.get():
            case "Physical Hazards (H2)":
                self.hide_frames()
                self.show_frame(self.h2_checkboxes_frame)
            case "Health Hazards (H3)":
                self.hide_frames()
                self.show_frame(self.h3_checkboxes_frame)
            case "Environmental Hazards (H4)":
                self.hide_frames()
                self.show_frame(self.h4_checkboxes_frame)

    def show_frame(self, frame):
        frame.grid(row=2, column=0, columnspan=2, padx=10, pady=5)

    def hide_frames(self):
        self.h2_checkboxes_frame.grid_forget()
        self.h3_checkboxes_frame.grid_forget()
        self.h4_checkboxes_frame.grid_forget()

    def load_checkboxes(self):
        if not self.checkbox_frames_generated:
            self.h2_checkboxes_frame.generate_checkboxes(
                "Physical Hazards (H2)"
            )
            self.h3_checkboxes_frame.generate_checkboxes("Health Hazards (H3)")
            self.h4_checkboxes_frame.generate_checkboxes(
                "Environmental Hazards (H4)"
            )
            self.checkbox_frames_generated = True

    def generate_hazard_checkboxes(self, hazard_type, frame):
        if self.get_hazards_callback is not None:
            hazards = self.get_hazards_callback(hazard_type)
            # Create checkboxes for each hazard
            for hazard in hazards:
                var = tk.BooleanVar()
                checkbox = tk.Checkbutton(
                    frame,
                    text=hazard,
                    variable=var,
                    bg=theme.BACKGROUND_COLOR,
                    fg=theme.TEXT_COLOR,
                    selectcolor=theme.BUTTON_COLOR,
                    command=lambda var=var: self.update_text_box(),
                )
                checkbox.pack(anchor="w", fill="x")
                # Keep track of checkbox vars and labels
                self.append_hazard_variables_callback(var, hazard)

    def update_text_box(self):
        text = ""
        if self.get_selected_hazards_callback is not None:
            hazard_vars = self.get_selected_hazards_callback()

        if hazard_vars is not None:
            for var, label in hazard_vars:
                if var.get():
                    text += f"{label}\n"
            self.text_box.delete("1.0", tk.END)  # Clear the existing text
            self.text_box.insert(tk.END, text)  # Insert the updated text


class HazardClassCheckboxes(tk.Frame):
    def __init__(self, parent, default_class=False):
        super().__init__(parent.checkboxes_container)

        self.parent = parent

        if default_class:
            self.grid(row=2, column=0, columnspan=2, padx=10, pady=5)

    def generate_checkboxes(self, hazard_class):
        parent = self.parent
        parent.generate_hazard_checkboxes(hazard_class, self)
