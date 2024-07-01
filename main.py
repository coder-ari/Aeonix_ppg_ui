import tkinter as tk
from tkinter import ttk, PhotoImage
import time
from settings_window2 import SettingsWindow
import datetime
import requests  # For making HTTP requests to fetch weather data
from PyQt5.QtWidgets import QApplication
import sys
from graph_window2 import MainWindow,PPGSettingsWidget



class DigitalClock(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
        self.weather_label = ttk.Label(self, font=('Helvetica', 25), anchor='e', foreground='white', background='black')
        self.weather_label.pack(side='top', anchor='ne', padx=50, pady=50, fill='x')

        self.label_time = ttk.Label(self, font=('Helvetica', 150, 'bold'), anchor='w', foreground='white', background='black')
        self.label_time.pack(expand=True, fill='both', padx=20)

        self.label_date = ttk.Label(self, font=('Helvetica', 20), anchor='w', foreground='white', background='black')
        self.label_date.pack(side='top', anchor='nw', padx=25, pady=10)

        #self.locale = tk.Locale()
        #self.locale.setlocale(tk.LC_ALL, 'en_US')

        self.custom_time = None
        self.custom_date = None
        self.location = 'Kolkata'
        self.update_time_date()
        self.update_weather()
    
    def update_time_date(self):
        if self.custom_time:
            current_time = self.custom_time.strftime('%H:%M:%S')
            self.custom_time += datetime.timedelta(seconds=1)
        else:
            current_time = time.strftime('%H:%M:%S')
        
        self.label_time.config(text=current_time)
        self.label_time.after(1000, self.update_time_date)

        if self.custom_date:
            current_date = self.custom_date.strftime('%A, %B %d, %Y')
        else:
            current_date = time.strftime('%A, %B %d, %Y')

        self.label_date.config(text=current_date)

    def set_time(self, new_time):
        self.custom_time = datetime.datetime.combine(datetime.date.today(), new_time)

    def set_date(self, new_date):
        if self.custom_time:
            self.custom_time = datetime.datetime.combine(new_date, self.custom_time.time())
        self.custom_date = new_date

    def set_location(self, new_location):
        self.location = new_location
        self.update_weather()

    def update_weather(self):
        api_key = 'f04abef8a0b64277b30125703241906'
        weather_url = f'http://api.weatherapi.com/v1/current.json?key={api_key}&q={self.location}&aqi=no'
        
        try:
            response = requests.get(weather_url)
            data = response.json()

            if 'error' in data:
                raise Exception(data['error']['message'])

            temp_c = data['current']['temp_c']
            condition = data['current']['condition']['text']

            weather_text = f'{temp_c}°C, {condition}'
            self.weather_label.config(text=weather_text)

        except Exception as e:
            print(f'Error fetching weather: {e}')
            self.weather_label.config(text='Weather unavailable')

        # Schedule the next update after 10 minutes (600000 ms)
        self.after(600000, self.update_weather)


class MainApplication(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.title('Digital Clock & Weather')
        self.configure(bg='black')

        # Set full screen
        self.attributes('-fullscreen', True)

        # Bind double-click event to exit
        self.bind('<Double-1>', self.exit_program)
        
        self.clock = DigitalClock(self, bg='black')
        self.clock.pack(expand=True, anchor='center')
        
        self.graph_icon = PhotoImage(file='graph.png')  
        self.settings_icon = PhotoImage(file='setting.png')  
        
        self.style = ttk.Style()
        self.style.configure('IconButton.TButton', background='black', foreground='white', borderwidth=0)
        
        self.graph_button = ttk.Button(self, image=self.graph_icon, style='IconButton.TButton', command=self.open_graph_window)
        self.graph_button.place(relx=0.2, rely=0.875, anchor='center')
        
        self.settings_button = ttk.Button(self, image=self.settings_icon, style='IconButton.TButton', command=self.open_settings_window)
        self.settings_button.place(relx=0.8, rely=0.875, anchor='center')

    def open_graph_window(self):
        #subprocess.Popen(['python', 'graph_window.py'])
        app = QApplication(sys.argv)
        window = MainWindow()        
        window.show()
        app.exec_()

    def open_settings_window(self):
        # SettingsWindow(self)
        app = QApplication(sys.argv)
        window = SettingsWindow()
        window.dateChanged.connect(self.clock.set_date)
        window.timeChanged.connect(self.clock.set_time)
        window.locationChanged.connect(self.clock.set_location)
        window.showFullScreen()  # Open in full-screen mode
        app.exec_()

    def exit_program(self, event=None):
        self.destroy()

if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()
