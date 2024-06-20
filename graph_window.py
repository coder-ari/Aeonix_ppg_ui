import tkinter as tk
from tkinter import ttk

class GraphWindow(tk.Toplevel):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.title("Graph")
        self.geometry("600x400")
        self.configure(bg='black')
        self.label = ttk.Label(self, text="Graph Window", font=('Helvetica', 20, 'bold'), foreground='white', background='black')
        self.label.pack(expand=True)
