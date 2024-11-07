from tkinter import Tk, filedialog, messagebox, ttk

from ttkbootstrap import Style

import views.chemical_frame as cf
import views.hazard_frame as hf
import views.precautions_frame as pf


class App(Tk):
    def __init__(self):
        # initializing the Tk class instance
        super().__init__()

        self.title("SoFab Inventory Managment System")

        self.style = Style(theme="darkly")

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
            self.hazard_frame.load_checkboxes()
        elif tab_text == "Precautionary Details":
            self.precautions_frame.load_checkboxes()
        else:
            pass

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

        controller.set_get_pdf_path_callback(self.get_file_path)

    def display_success(self, message):
        messagebox.showinfo("Success!", message)

    def display_error(self, error_message):
        messagebox.showerror("ERROR", error_message)

    def get_file_path(self):
        return filedialog.askopenfilename(
            title="Select a Directory", filetypes=".pdf"
        )
