import datetime
import tkinter as tk
from tkinter import ttk

class SettingsWindow(tk.Toplevel):
    def __init__(self, parent, clock, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
        self.clock = clock
        self.title("Settings")
        self.geometry("400x400")
        self.configure(bg='black')

        self.label = ttk.Label(self, text="Settings Window", font=('Helvetica', 20, 'bold'), foreground='white', background='black')
        self.label.pack(pady=10)

        self.location_label = ttk.Label(self, text="Location:", font=('Helvetica', 12), foreground='white', background='black')
        self.location_label.pack(pady=5)

        self.location_var = tk.StringVar()
        self.location_var.set(self.clock.location)  # Set current location in entry
        self.location_entry = ttk.Entry(self, textvariable=self.location_var, font=('Helvetica', 12))
        self.location_entry.pack(padx=20, pady=5)

        self.save_button = ttk.Button(self, text="Save", command=self.save_settings)
        self.save_button.pack(pady=10)

        self.style = ttk.Style()
        self.style.configure("TLabel", background="black", foreground="white")
        self.style.configure("TEntry", fieldbackground="black", foreground="white")
        self.style.configure("TButton", background="black", foreground="white")

        self.time_frame = ttk.Frame(self, padding="10 10 10 10", style="Settings.TFrame")
        self.time_frame.pack(expand=True)

        self.hour_var = tk.StringVar()
        self.minute_var = tk.StringVar()
        self.second_var = tk.StringVar()

        self.hour_combo = ttk.Combobox(self.time_frame, width=3, textvariable=self.hour_var, font=('Helvetica', 20))
        self.hour_combo['values'] = [f'{i:02d}' for i in range(24)]
        self.hour_combo.grid(column=1, row=1)

        self.minute_combo = ttk.Combobox(self.time_frame, width=3, textvariable=self.minute_var, font=('Helvetica', 20))
        self.minute_combo['values'] = [f'{i:02d}' for i in range(60)]
        self.minute_combo.grid(column=2, row=1)

        self.second_combo = ttk.Combobox(self.time_frame, width=3, textvariable=self.second_var, font=('Helvetica', 20))
        self.second_combo['values'] = [f'{i:02d}' for i in range(60)]
        self.second_combo.grid(column=3, row=1)

        self.set_time_button = ttk.Button(self.time_frame, text="Set Time", command=self.set_time)
        self.set_time_button.grid(column=1, row=2, columnspan=3, pady=10)

        self.date_frame = ttk.Frame(self, padding="10 10 10 10", style="Settings.TFrame")
        self.date_frame.pack(expand=True)

        self.day_var = tk.StringVar()
        self.month_var = tk.StringVar()
        self.year_var = tk.StringVar()
        self.weekday_var = tk.StringVar()

        self.day_combo = ttk.Combobox(self.date_frame, width=3, textvariable=self.day_var, font=('Helvetica', 20))
        self.day_combo['values'] = [f'{i:02d}' for i in range(1, 32)]
        self.day_combo.grid(column=1, row=1)

        self.month_combo = ttk.Combobox(self.date_frame, width=3, textvariable=self.month_var, font=('Helvetica', 20))
        self.month_combo['values'] = [f'{i:02d}' for i in range(1, 13)]
        self.month_combo.grid(column=2, row=1)

        self.year_combo = ttk.Combobox(self.date_frame, width=5, textvariable=self.year_var, font=('Helvetica', 20))
        self.year_combo['values'] = [str(i) for i in range(2000, 2101)]
        self.year_combo.grid(column=3, row=1)

        self.set_date_button = ttk.Button(self.date_frame, text="Set Date", command=self.set_date)
        self.set_date_button.grid(column=1, row=2, columnspan=3, pady=10)

        self.weekday_label = ttk.Label(self.date_frame, textvariable=self.weekday_var, font=('Helvetica', 14), foreground='white', background='black')
        self.weekday_label.grid(column=1, row=3, columnspan=3, pady=5)

        self.style.configure("Settings.TFrame", background="black")
        self.style.configure("TCombobox", fieldbackground="black", foreground="white")

    def save_settings(self):
        new_location = self.location_var.get()
        self.clock.set_location(new_location)
        print(f"New location saved: {new_location}")
        self.destroy()

    def set_time(self):
        try:
            hours = int(self.hour_var.get())
            minutes = int(self.minute_var.get())
            seconds = int(self.second_var.get())
            new_time = datetime.datetime.now().replace(hour=hours, minute=minutes, second=seconds, microsecond=0)
            self.clock.set_time(new_time)
        except ValueError:
            print("Invalid time entered")
        self.destroy()

    def set_date(self):
        try:
            day = int(self.day_var.get())
            month = int(self.month_var.get())
            year = int(self.year_var.get())

            # Calculate weekday
            weekday_name = datetime.datetime(year, month, day).strftime('%A')
            self.weekday_var.set(f"Weekday: {weekday_name}")

            new_date = datetime.datetime(year, month, day)
            self.clock.set_date(new_date)
        except ValueError:
            print("Invalid date entered")
        self.destroy()
