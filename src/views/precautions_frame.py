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
        self.precaution_box = tk.Text(
            self,
            height=5,
            width=40,
            bg=theme.ENTRY_COLOR,
            fg=theme.TEXT_COLOR,
            insertbackground=theme.TEXT_COLOR,
        )
        self.precaution_box.grid(
            row=1, column=0, columnspan=2, padx=10, pady=5
        )

        # Generate PDF button
        self.generate_button = tk.Button(
            self,
            text="Generate PDF",
            command=self.on_submit,
            bg=theme.BUTTON_COLOR,
            fg=theme.TEXT_COLOR,
        )
        self.generate_button.grid(
            row=3, column=0, columnspan=2, padx=10, pady=10
        )

        self.precaution_checkboxes_frame = Precaution_checkboxes(self)

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
                )
                checkbox.pack(anchor="w")
                # Keep track of checkbox vars and labels

                self.checkbox_vars.append((var, precaution))

        # Add functionality to update text box based on checkboxes
        # update_text_box()


class Precaution_checkboxes(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.grid(row=2, column=0, columnspan=2, padx=10, pady=5)
        #  List to keep track of precaution checkbox variables
        self.precaution_checkbox_vars = []

        parent.precaution_type_var.trace_add(
            "write",
            lambda *args: parent.generate_precautionary_checkboxes(self),
        )
