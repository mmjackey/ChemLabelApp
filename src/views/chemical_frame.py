import tkinter as tk
from tkinter import ttk


# Setting up first tab for Chemical Details
class Chemical_frame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.submit_callback = None

        parent.notebook.add(self, text="Chemical Details")

        # Configure grid weights
        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        self.entries_containter = tk.Frame(self)
        self.entries_containter.grid(row=0, column=0)

        self.chem_name_label = ttk.Label(
            self.entries_containter,
            text="Chemical Name:",
        )
        self.chem_name_label.grid(row=0, column=0, padx=10, pady=5)

        self.batch_entry = ttk.Entry(self.entries_containter)
        self.batch_entry.grid(row=0, column=1, padx=10, pady=5)

        self.volume_label = ttk.Label(self.entries_containter, text="Volume:")
        self.volume_label.grid(row=1, column=0, padx=10, pady=5)

        self.volume_entry = ttk.Entry(self.entries_containter)
        self.volume_entry.grid(row=1, column=1, padx=10, pady=5)

        self.concentration_label = ttk.Label(
            self.entries_containter, text="Concentration:"
        )
        self.concentration_label.grid(row=2, column=0, padx=10, pady=5)

        self.concentration_entry = ttk.Entry(self.entries_containter)
        self.concentration_entry.grid(row=2, column=1, padx=10, pady=5)

        self.date_created_label = ttk.Label(
            self.entries_containter, text="Date Created:"
        )
        self.date_created_label.grid(row=4, column=0, padx=10, pady=5)

        self.date_entry = ttk.Entry(self.entries_containter)
        self.date_entry.grid(row=4, column=1, padx=10, pady=5)

        self.barcode_input_label = ttk.Label(
            self.entries_containter, text="Barcode Input:"
        )
        self.barcode_input_label.grid(row=5, column=0, padx=10, pady=5)

        self.barcode_entry = ttk.Entry(self.entries_containter)
        self.barcode_entry.grid(row=5, column=1, padx=10, pady=5)

        self.qr_code_input = ttk.Label(
            self.entries_containter, text="QR Code Input:"
        )
        self.qr_code_input.grid(row=6, column=0, padx=10, pady=5)

        self.qr_code_entry = ttk.Entry(self.entries_containter)
        self.qr_code_entry.grid(row=6, column=1, padx=10, pady=5)

        self.qr_code_entry.insert(
            0,
            "https://drive.google.com/file/d/1HfsqJG-goraXZHW8OwokIUNG_nVDM_Uz/view",
        )

        # Page size selection
        self.page_size_label = ttk.Label(
            self.entries_containter, text="Page Size:"
        )
        self.page_size_label.grid(row=7, column=0, padx=10, pady=5)

        self.page_size_var = tk.StringVar(value="Portrait")  # Default value

        self.page_size_menu = ttk.Combobox(
            self.entries_containter,
            textvariable=self.page_size_var,
            values=["Portrait", "Portrait", "Landscape"],
        )

        self.page_size_menu.grid(row=7, column=1, padx=10, pady=5)

        self.stage_selection_label = ttk.Label(
            self.entries_containter, text="Stage:"
        )
        self.stage_selection_label.grid(row=9, column=0, padx=5, pady=5)

        self.stage_choice = tk.StringVar(value="Synthesis")
        options = [
            "Synthesis",
            "Washing",
            "Drying",
            "Synthesis",
            "Functionalization",
            "Quality Control",
            "Shipping",
        ]

        self.stage_entry = ttk.Combobox(
            self.entries_containter,
            textvariable=self.stage_choice,
            values=options,
        )

        self.stage_entry.grid(row=9, column=1, padx=5, pady=5)

        self.checkbox_var = tk.BooleanVar()
        self.checkbox = ttk.Checkbutton(
            self.entries_containter,
            text="Add to database",
            variable=self.checkbox_var,
            command=self.checkbox_checked,
        )

        self.checkbox.grid(row=8, column=0, padx=10, pady=5)

        # Configure grid weights
        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

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
