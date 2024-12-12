from customtkinter import *
import tkinter as tk
from tkinter import ttk


class ItemFrameContainer(tk.Frame):
    def __init__(self, controller, item_types):
        super().__init__()

        self.controller = controller

        self.item_types = item_types

        """
        Configure grid weights so that the items expand and contract with
        window
        """

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)

        first_key = list(item_types.keys())[0]

        self.item_type_var = tk.StringVar(value=first_key)  # Default value

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

        self.table_names = table_names

        self.entry_vars = {}

        #Scrollbar Additions
        # self.canvas = tk.Canvas(self,height=700)
        # self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        # self.canvas.configure(yscrollcommand=self.scrollbar.set)
        # self.grid_rowconfigure(0, weight=1)
        # self.grid_columnconfigure(0, weight=1)
        
        # self.canvas.grid(row=0, column=0, sticky="nsew")
        # self.scrollbar.grid(row=0, column=1, sticky="ns")
        
        self.entries_containter = CTkFrame(self)
        self.entries_containter.grid(row=0, column=0)

        # self.canvas.create_window((0, 0), window=self.entries_containter, anchor="nw")

        # self.entries_containter.bind("<Configure>", self.on_frame_configure)

        # print("Width:", self.canvas.winfo_width())
        # print("Height:", self.canvas.winfo_height())

        self.add_content()

        self.checkbox_var = tk.BooleanVar()
        self.checkbox = CTkCheckBox(
            self.entries_containter,
            text="Add to database",
            variable=self.checkbox_var,
        )

        checkbox_location = self.entries_containter.grid_size()[1]

        self.checkbox.grid(row=checkbox_location, column=1, padx=10, pady=5)

    def add_content(self):
        print(self.table_names)
        table_columns_dict = self.controller.get_database_column_names(
            self.table_names
        )

        """
        for each type of item (general product, general inventory, or chemical inventory),
        we query each of the tables associated with these items and dynamicall print
        a label and an entry for each column in each table
        """

        for i, (key, column_list) in enumerate(table_columns_dict.items()):
            table_label_text = self.label_tables(key, i)

            formatted_table_columns = self.format_names(column_list)
            for j, column in enumerate(column_list):
                if "id" in column.lower() or "hazard" in column.lower():
                    continue
                elif "fk" in column.lower():
                    words = column.lower().split("_")
                    words.remove("fk")
                    for word in words:
                        if word in table_label_text.lower():
                            words.remove(word)
                    # whatever remains after removing the label text
                    # and fk, should be the contents of the entry box
                    formatted_table_columns[j] = words[0].title()

                label = CTkLabel(
                    self.entries_containter,
                    text=formatted_table_columns[j],
                )
                label.grid(row=2 * j, column=i, padx=10, pady=5)

                entry = CTkEntry(self.entries_containter)
                entry.grid(row=2 * j + 1, column=i, padx=10, pady=5)

                self.entry_vars[column] = entry

    def label_tables(self, key, i):
        table_label_text = f"{self.format_names(key)} \n    Information"

        self.table_label = CTkLabel(
            self.entries_containter,
            text=table_label_text,
        )
        self.table_label.grid(row=0, column=i)
        return table_label_text

    def format_names(self, names):
        if type(names) is list:
            return [name.replace("_", " ").title() for name in names]
        elif type(names) is str:
            return names.replace("_", " ").title()

    def on_frame_configure(self, event):
        """Update scroll region when the content frame is resized."""
        self.canvas.config(scrollregion=self.canvas.bbox("all"))