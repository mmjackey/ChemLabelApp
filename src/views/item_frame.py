import tkinter as tk
from tkinter import ttk


class ItemFrameContainer(tk.Frame):
    def __init__(self, controller, item_types):
        super().__init__()

        self.controller = controller

        """
        Configure grid weights so that the items expand and contract with
        window
        """

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)

        self.item_type_var = tk.StringVar(
            value="Chemical Inventory"
        )  # Default value

        self.item_type_menu = tk.OptionMenu(
            self, self.item_type_var, *item_types.keys()
        )

        self.item_type_menu.grid(row=0, column=1, padx=10, pady=5)

        self.select_item_type_label = ttk.Label(self, text="Select Item Type:")
        self.select_item_type_label.grid(row=0, column=0, padx=10, pady=5)

        self.item_type_frames = {}

        """
        for each item type (chemical inventory, general, batch),
        create a frame that can hold all of the potential entry
        boxes that you could need for those tables
        """

        for i, item_type in enumerate(list(item_types.keys())):
            # on the first iteration (first key), make it the default type so
            # it shows up when you open the tab
            if i == 0:
                frame = ItemFrame(
                    self,
                    self.controller,
                    item_types[item_type],
                    default_type=True,
                )
            else:
                # create, the frame and pass in the table names for the item_type
                frame = ItemFrame(self, self.controller, item_types[item_type])
            self.item_type_frames[item_type] = frame

        self.item_type_var.trace_add(
            "write",
            lambda *args: self.switch_frame(),
        )

    def switch_frame(self):
        frame = self.item_type_var.get()
        self.hide_frames()
        self.show_frame(self.item_type_frames[frame])

    def hide_frames(self):
        for frame in self.item_type_frames.values():
            frame.grid_forget()

    def show_frame(self, frame):
        frame.grid(row=2, column=0, columnspan=2, padx=10, pady=5)


# Setting up first tab for item Details
class ItemFrame(tk.Frame):
    def __init__(self, parent, controller, table_names, default_type=False):
        super().__init__(parent)
        if default_type:
            self.grid(row=2, column=0, columnspan=2, padx=10, pady=5)

        self.controller = controller

        self.entry_vars = {}

        self.entries_containter = tk.Frame(self)
        self.entries_containter.grid(row=0, column=0)

        table_columns_dict = self.controller.get_database_column_names(
            table_names
        )

        for i, (key, column_list) in enumerate(table_columns_dict.items()):
            formatted_table_columns = [
                col.replace("_", " ").title() for col in column_list
            ]
            for j, column in enumerate(column_list):
                label = ttk.Label(
                    self.entries_containter,
                    text=formatted_table_columns[j],
                )
                label.grid(row=2 * j, column=i, padx=10, pady=5)

                entry = ttk.Entry(self.entries_containter)
                entry.grid(row=2 * j + 1, column=i, padx=10, pady=5)

                self.entry_vars[column] = entry

        self.checkbox_var = tk.BooleanVar()
        self.checkbox = ttk.Checkbutton(
            self.entries_containter,
            text="Add to database",
            variable=self.checkbox_var,
            command=self.checkbox_checked,
        )

        checkbox_location = self.entries_containter.grid_size()[1]

        self.checkbox.grid(row=checkbox_location, column=1, padx=10, pady=5)

    def get_item_details(self):
        details = {
            "name": self.batch_entry.get(),
            "volume": self.volume_entry.get(),
            "concentration": self.concentration_entry.get(),
            "barcode input": self.barcode_entry.get(),
            "qr code input": self.qr_code_entry.get(),
            "page size": self.page_size_var.get(),
            "stage": self.stage_entry.get(),
        }
        return details

    def checkbox_checked(self):
        if self.checkbox_var.get():
            pass
        else:
            pass
