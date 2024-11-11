from tkinter import Tk, filedialog, messagebox, ttk

from ttkbootstrap import Style

from views.item_frame import ItemFrameContainer
from views.submission_frame import SubmitFrame
from views.warning_frame import HazardPrecautionFrame


class App(Tk):
    def __init__(self, controller):
        # initializing the Tk class instance
        super().__init__()

        self.title("SoFab Inventory Managment System")

        self.style = Style(theme="darkly")

        self.controller = controller
        self.controller.set_view(self)

        self.notebook = ttk.Notebook()
        self.notebook.pack(fill="both", expand=True)
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_selection)

        # filling the notebook (top tabs) with frames

        item_type_tables = self.controller.get_item_type_tables()

        self.item_frame_container = ItemFrameContainer(
            controller, item_type_tables
        )
        self.notebook.add(self.item_frame_container, text="Item Details")

        hazard_warnings = self.controller.get_hazard_classes_dict()

        self.hazard_frame = HazardPrecautionFrame(
            self, controller, warning_dict=hazard_warnings
        )
        self.notebook.add(self.hazard_frame, text="Hazard Details")

        precaution_warnings = self.controller.get_precaution_classes_dict()

        self.precautions_frame = HazardPrecautionFrame(
            self, controller, warning_dict=precaution_warnings
        )
        self.notebook.add(self.precautions_frame, text="Precautionary Details")

        hazard_diamonds = self.controller.get_hazard_diamonds_dict()

        self.hazard_diamonds_frame = HazardPrecautionFrame(
            self, controller, warning_dict=hazard_diamonds, images=True
        )

        self.notebook.add(self.hazard_diamonds_frame, text="Hazard Diamonds")

        self.submit_frame = SubmitFrame(controller)
        self.notebook.add(self.submit_frame, text="Submission Frame")

    def on_tab_selection(self, event):
        selected_tab = event.widget.select()
        tab_text = event.widget.tab(selected_tab, "text")

        if tab_text == "Hazard Details":
            pass
        elif tab_text == "Precautionary Details":
            pass
        else:
            pass

    def display_success(self, message):
        messagebox.showinfo("Success!", message)

    def display_error(self, error_message):
        messagebox.showerror("ERROR", error_message)

    def get_file_path(self):
        return filedialog.askopenfilename(
            title="Select a Directory", filetypes=".pdf"
        )
