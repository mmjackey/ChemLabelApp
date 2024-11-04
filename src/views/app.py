from tkinter import Tk, messagebox, ttk

import theme
import views.chemical_frame as cf
import views.hazard_frame as hf
import views.precautions_frame as pf


class App(Tk):
    def __init__(self):
        # initializing the Tk class instance
        super().__init__()

        self.title("SoFab Inventory Managment System")

        # Initialize styles
        self.style = ttk.Style(self)
        self.style.configure("TFrame", background=theme.BACKGROUND_COLOR)
        self.style.configure("TNotebook", background=theme.BACKGROUND_COLOR)
        self.style.configure(
            "TNotebook.Tab",
            background=theme.BUTTON_COLOR,
            foreground=theme.TEXT_COLOR,
        )
        self.style.configure(
            "TButton",
            background=theme.BUTTON_COLOR,
            foreground=theme.TEXT_COLOR,
        )
        self.style.configure(
            "TLabel",
            background=theme.BACKGROUND_COLOR,
            foreground=theme.TEXT_COLOR,
        )
        self.notebook = ttk.Notebook()
        self.notebook.pack(fill="both", expand=True)
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_selection)

        self.chemical_frame = cf.Chemical_frame(self)
        self.hazard_frame = hf.Hazard_frame(self)
        self.precautions_frame = pf.Precautions_frame(self)

    def on_tab_selection(self, event):
        selected_tab = event.widget.select()
        tab_text = event.widget.tab(selected_tab, "text")

        if tab_text == "Hazard Details":
            self.hazard_frame.load_default_checkboxes()

    def set_callbacks(self, controller):
        self.chemical_frame.submit_callback = controller.handle_submit_pdf

        self.hazard_frame.get_hazards_callback = controller.get_hazards

        self.hazard_frame.get_selected_hazards_callback = (
            controller.get_selected_hazards
        )
        self.hazard_frame.append_hazard_variables_callback = (
            controller.append_hazard_variables
        )

        self.precautions_frame.get_precautions_callback = (
            controller.get_precautions
        )

        self.precautions_frame.get_selected_precautions_callback = (
            controller.get_selected_precautions
        )

        self.precautions_frame.append_precautions_variables = (
            controller.append_precautions_variables
        )
        self.precautions_frame.submission_callback = controller.on_submission

    def display_success(self, message):
        messagebox.showinfo("Success!", message)

    def display_error(self, error_message):
        messagebox.showerror("ERROR", error_message)
