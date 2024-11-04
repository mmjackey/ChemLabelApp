import tkinter as tk

import theme


class Precautions_frame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        #  Third tab for Precautionary Type
        parent.notebook.add(self, text="Precautionary Details")

        # Precautionary Type selection
        self.precaution_type_var = tk.StringVar(value="P1")  # Default value
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
        generate_button = tk.Button(
            self,
            text="Generate PDF",
            command=self.on_submit,
            bg=theme.BUTTON_COLOR,
            fg=theme.TEXT_COLOR,
        )
        generate_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10)
        self.precaution_checkboxes_frame = Precaution_checkboxes(self)

    def on_submit(self, parent):
        batch = parent.Chemical_frame.batch_entry.get()
        #    size = size_entry.get()
        date = parent.Chemical_frame.date_entry.get()
        volume = parent.Chemical_frame.volume_entry.get()
        concentration = parent.Chemical_frame.concentration_entry.get()
        barcode_input = parent.Chemical_frame.barcode_entry.get()
        qr_code_input = parent.Chemical_frame.qr_code_entry.get()
        page_size_option = parent.Chemical_frame.page_size_var.get()
        stage = parent.Chemical_frame.stage_choice.get()

        print(
            batch,
            date,
            volume,
            concentration,
            barcode_input,
            qr_code_input,
            page_size_option,
            stage,
        )

        # text = text_box.get(
        #    "1.0", tk.END
        # ).strip()  # Get text from the Text widget
        ## Get precautions from the Text widget
        ## precautions = precaution_box.get("1.0", tk.END).strip()

        ## Set page size based on user selection
        # page_size = landscape(A4) if page_size_option == "Landscape" else A4

        # barcode_path = parent.pdf_generator.generate_barcode(barcode_input)
        # qr_code_path = parent.pdf_generator.generate_qr_code(qr_code_input)

        ## Add barcode batch id to database
        # print_synthesis_rows(barcode_input.upper(), stage)

        # generate_pdf(
        #    batch,
        #    date,
        #    concentration,
        #    volume,
        #    barcode_path,
        #    qr_code_path,
        #    page_size,
        #    text,
        # )

        # messagebox.showinfo("Success", "PDF generated successfully!")


class Precaution_checkboxes(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.grid(row=2, column=0, columnspan=2, padx=10, pady=5)
        #  List to keep track of precaution checkbox variables
        self.precaution_checkbox_vars = []

        # parent.precaution_type_var.trace_add(
        #    "write",
        #    lambda *args: update_precautionary_checkboxes(self),
        # )
