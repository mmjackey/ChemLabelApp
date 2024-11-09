from tkinter import Tk, filedialog, messagebox, ttk

from ttkbootstrap import Style

from views.item_frame import ItemFrameContainer
from views.warning_frame import HazardPrecautionFrame


class App(Tk):
    def __init__(self, controller):
        # initializing the Tk class instance
        super().__init__()

        self.title("SoFab Inventory Managment System")

        self.style = Style(theme="darkly")

        self.controller = controller

        self.notebook = ttk.Notebook()
        self.notebook.pack(fill="both", expand=True)
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_selection)

        item_types = {
            "Chemical Inventory": ["chemical_inventory", "general_product"],
            "General Inventory": ["general_inventory", "general_product"],
            "Product Inventory (Batch Process)": [
                "batch_inventory",
                "synthesis",
                "washing",
                "drying",
                "functionalization",
                "quality_control",
                "shipping",
            ],
        }

        self.item_frame_container = ItemFrameContainer(controller, item_types)
        self.notebook.add(self.item_frame_container, text="Item Details")

        self.hazard_frame = HazardPrecautionFrame(
            self, controller, self.controller.get_hazard_classes_dict()
        )
        self.notebook.add(self.hazard_frame, text="Hazard Details")

        self.precautions_frame = HazardPrecautionFrame(
            self, controller, self.controller.get_precaution_classes_dict()
        )
        self.notebook.add(self.precautions_frame, text="Precautionary Details")

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
