import tkinter as tk
from tkinter import ttk

import theme


# Setting up first tab for Chemical Details
class Chemical_frame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.submit_callback = None

        parent.notebook.add(self, text="Chemical Details")

        self.chem_name_label = tk.Label(
            self,
            text="Chemical Name:",
            bg=theme.BACKGROUND_COLOR,
            fg=theme.TEXT_COLOR,
        )
        self.chem_name_label.grid(row=0, column=0, padx=10, pady=5)

        self.batch_entry = tk.Entry(
            self, bg=theme.ENTRY_COLOR, fg=theme.TEXT_COLOR
        )
        self.batch_entry.grid(row=0, column=1, padx=10, pady=5)

        self.volume_label = tk.Label(
            self,
            text="Volume:",
            bg=theme.BACKGROUND_COLOR,
            fg=theme.TEXT_COLOR,
        )
        self.volume_label.grid(row=1, column=0, padx=10, pady=5)

        self.volume_entry = tk.Entry(
            self, bg=theme.ENTRY_COLOR, fg=theme.TEXT_COLOR
        )

        self.volume_entry.grid(row=1, column=1, padx=10, pady=5)

        self.concentration_label = tk.Label(
            self,
            text="Concentration:",
            bg=theme.BACKGROUND_COLOR,
            fg=theme.TEXT_COLOR,
        )
        self.concentration_label.grid(row=2, column=0, padx=10, pady=5)

        self.concentration_entry = tk.Entry(
            self, bg=theme.ENTRY_COLOR, fg=theme.TEXT_COLOR
        )
        self.concentration_entry.grid(row=2, column=1, padx=10, pady=5)

        self.date_created_label = tk.Label(
            self,
            text="Date Created:",
            bg=theme.BACKGROUND_COLOR,
            fg=theme.TEXT_COLOR,
        )
        self.date_created_label.grid(row=4, column=0, padx=10, pady=5)

        self.date_entry = tk.Entry(
            self, bg=theme.ENTRY_COLOR, fg=theme.TEXT_COLOR
        )
        self.date_entry.grid(row=4, column=1, padx=10, pady=5)

        self.barcode_input_label = tk.Label(
            self,
            text="Barcode Input:",
            bg=theme.BACKGROUND_COLOR,
            fg=theme.TEXT_COLOR,
        )
        self.barcode_input_label.grid(row=5, column=0, padx=10, pady=5)

        self.barcode_entry = tk.Entry(
            self, bg=theme.ENTRY_COLOR, fg=theme.TEXT_COLOR
        )
        self.barcode_entry.grid(row=5, column=1, padx=10, pady=5)

        self.qr_code_input = tk.Label(
            self,
            text="QR Code Input:",
            bg=theme.BACKGROUND_COLOR,
            fg=theme.TEXT_COLOR,
        )

        self.qr_code_input.grid(row=6, column=0, padx=10, pady=5)

        self.qr_code_entry = tk.Entry(
            self, bg=theme.ENTRY_COLOR, fg=theme.TEXT_COLOR
        )
        self.qr_code_entry.grid(row=6, column=1, padx=10, pady=5)

        self.qr_code_entry.insert(
            0,
            "https://drive.google.com/file/d/1HfsqJG-goraXZHW8OwokIUNG_nVDM_Uz/view",
        )

        # Page size selection
        self.page_size_label = tk.Label(
            self,
            text="Page Size:",
            bg=theme.BACKGROUND_COLOR,
            fg=theme.TEXT_COLOR,
        )
        self.page_size_label.grid(row=7, column=0, padx=10, pady=5)

        self.page_size_var = tk.StringVar(value="Portrait")  # Default value

        self.page_size_menu = ttk.OptionMenu(
            self, self.page_size_var, "Portrait", "Portrait", "Landscape"
        )

        self.page_size_menu.grid(row=7, column=1, padx=10, pady=5)

        self.stage_selection_label = tk.Label(
            self, text="Stage:", bg=theme.BACKGROUND_COLOR, fg=theme.TEXT_COLOR
        ).grid(row=9, column=0, padx=5, pady=5)

        self.stage_choice = tk.StringVar()
        options = ["Synthesis", "Washing"]

        self.stage_entry = ttk.OptionMenu(
            self, self.stage_choice, options[0], *options
        )

        self.stage_entry.grid(row=9, column=1, padx=5, pady=5)

        self.checkbox_var = tk.BooleanVar()
        self.checkbox = tk.Checkbutton(
            self,
            text="Add to database",
            variable=self.checkbox_var,
            command=self.checkbox_checked,
        )

        self.checkbox.grid(row=8, column=0, padx=10, pady=5)

    def checkbox_checked(self):
        if self.checkbox_var.get():
            pass
        else:
            pass

    def update_text_box(self, parent):
        text = ""
        for var, label in self.checkbox_vars:
            if var.get():
                text += f"{label}\n"
        parent.text_box.delete("1.0", tk.END)  # Clear the existing text
        parent.text_box.insert(tk.END, text)  # Insert the updated text
