import tkinter as tk
from tkinter import ttk


class SubmitFrame(tk.Frame):
    def __init__(self, controller):
        super().__init__()

        self.controller = controller

        self.button = ttk.Button(
            self,
            text="Generate PDF",
            command=lambda: self.controller.on_submission(),
        )
        self.button.pack()
