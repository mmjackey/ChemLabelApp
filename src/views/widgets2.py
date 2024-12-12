import customtkinter
import tkinter as tk
from tkinter import ttk

from PIL import Image, ImageTk
from reportlab.lib.pagesizes import A4, landscape
from config import AppConfig

class DetailSelectFrame(customtkinter.CTkFrame):
    def __init__(self, tab_frame, controller, tables):
        super().__init__(tab_frame)
        self.controller = controller

        self.area_1_header = customtkinter.CTkLabel(
            self,
            text=tab_frame,
            font=customtkinter.CTkFont(size=18, weight="bold"),
        )
        self.area_1_header.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        