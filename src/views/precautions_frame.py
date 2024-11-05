import tkinter as tk

import theme


class Precautions_frame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        #  Third tab for Precautionary Type
        parent.notebook.add(self, text="Precautionary Details")

        self.submission_callback = None
        self.get_precautions_callback = None
        self.get_selected_precautions_callback = None
        self.append_precautions_variables = None

        self.checkbox_frames_generated = False

        # Precautionary Type selection
        self.precaution_type_var = tk.StringVar(
            value="General precautionary statements (P1)"
        )  # Default value

        self.precaution_type_var.trace_add(
            "write",
            lambda *args: self.switch_frame(),
        )

        self.precaution_type_menu = tk.OptionMenu(
            self,
            self.precaution_type_var,
            "General precautionary statements (P1)",
            "Prevention precautionary statements (P2)",
            "Response precautionary statements (P3)",
            "Storage precautionary statements (P4)",
            "Disposal precautionary statements (P5)",
        )

        self.precaution_type_menu.config(
            bg=theme.BUTTON_COLOR,
            fg=theme.TEXT_COLOR,
            activebackground=theme.HIGHLIGHT_COLOR,
        )

        self.precaution_type_label = tk.Label(
            self,
            text="Select Precautionary Type:",
            bg=theme.BACKGROUND_COLOR,
            fg=theme.TEXT_COLOR,
        )
        self.precaution_type_label.grid(row=0, column=0, padx=10, pady=5)

        self.precaution_type_menu.grid(row=0, column=1, padx=10, pady=5)

        # Precaution description text box
        self.text_box = tk.Text(
            self,
            height=5,
            width=40,
            bg=theme.ENTRY_COLOR,
            fg=theme.TEXT_COLOR,
            insertbackground=theme.TEXT_COLOR,
        )
        self.text_box.grid(row=1, column=0, columnspan=2, padx=10, pady=5)

        # Generate PDF button
        self.generate_button = tk.Button(
            self,
            text="Generate PDF",
            command=self.submission_callback,
            bg=theme.BUTTON_COLOR,
            fg=theme.TEXT_COLOR,
        )
        self.generate_button.grid(
            row=3, column=0, columnspan=2, padx=10, pady=10
        )

        self.p1_checkboxes_frame = PrecautionClassCheckboxes(
            self, default_class=True
        )
        self.p2_checkboxes_frame = PrecautionClassCheckboxes(self)
        self.p3_checkboxes_frame = PrecautionClassCheckboxes(self)
        self.p4_checkboxes_frame = PrecautionClassCheckboxes(self)
        self.p5_checkboxes_frame = PrecautionClassCheckboxes(self)

    def switch_frame(self):
        match (self.precaution_type_var.get()):
            case "General precautionary statements (P1)":
                self.hide_frames()
                self.show_frame(self.p1_checkboxes_frame)
            case "Prevention precautionary statements (P2)":
                self.hide_frames()
                self.show_frame(self.p2_checkboxes_frame)
            case "Response precautionary statements (P3)":
                self.hide_frames()
                self.show_frame(self.p3_checkboxes_frame)
            case "Storage precautionary statements (P4)":
                self.hide_frames()
                self.show_frame(self.p4_checkboxes_frame)
            case "Disposal precautionary statements (P5)":
                self.hide_frames()
                self.show_frame(self.p5_checkboxes_frame)

    def show_frame(self, frame):
        frame.grid(row=2, column=0, columnspan=2, padx=10, pady=5)

    def hide_frames(self):
        self.p1_checkboxes_frame.grid_forget()
        self.p2_checkboxes_frame.grid_forget()
        self.p3_checkboxes_frame.grid_forget()
        self.p4_checkboxes_frame.grid_forget()
        self.p5_checkboxes_frame.grid_forget()

    def load_checkboxes(self):
        if not self.checkbox_frames_generated:
            self.p1_checkboxes_frame.generate_checkboxes(
                "General precautionary statements (P1)"
            )
            self.p2_checkboxes_frame.generate_checkboxes(
                "Prevention precautionary statements (P2)"
            )
            self.p3_checkboxes_frame.generate_checkboxes(
                "Response precautionary statements (P3)"
            )
            self.p4_checkboxes_frame.generate_checkboxes(
                "Storage precautionary statements (P4)"
            )
            self.p5_checkboxes_frame.generate_checkboxes(
                "Disposal precautionary statements (P5)"
            )

    def generate_precautionary_checkboxes(
        self, precaution_type, precaution_checkbox_frame
    ):
        if self.get_precautions_callback is not None:
            precautions = self.get_precautions_callback(precaution_type)
            for precaution in precautions:
                var = tk.BooleanVar()
                checkbox = tk.Checkbutton(
                    precaution_checkbox_frame,
                    text=precaution,
                    variable=var,
                    bg=theme.BACKGROUND_COLOR,
                    fg=theme.TEXT_COLOR,
                    selectcolor=theme.BUTTON_COLOR,
                    command=lambda: self.update_text_box(),
                )
                checkbox.pack(anchor="w", fill="x")
                # Keep track of checkbox vars and labels
                self.append_precautions_variables(var, precaution)

    def update_text_box(self):
        text = ""
        if self.get_selected_precautions_callback is not None:
            precaution_vars = self.get_selected_precautions_callback()

        if precaution_vars is not None:
            for var, label in precaution_vars:
                if var.get():
                    text += f"{label}\n"
            self.text_box.delete("1.0", tk.END)  # Clear the existing text
            self.text_box.insert(tk.END, text)  # Insert the updated text


class PrecautionClassCheckboxes(tk.Frame):
    def __init__(self, parent, default_class=False):
        super().__init__(parent)

        self.parent = parent

        if default_class:
            self.grid(row=2, column=0, columnspan=2, padx=10, pady=5)

    def generate_checkboxes(self, precaution_class):
        parent = self.parent

        parent.generate_precautionary_checkboxes(precaution_class, self)
