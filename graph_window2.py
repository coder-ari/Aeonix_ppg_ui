import sys
import serial
from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QApplication
from PyQt5.QtCore import Qt, QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import threading
import time
import os
from settings_window2 import PPGSettingsWidget

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=9, height=7, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor('black')  # Set graph background to black
        super(MplCanvas, self).__init__(self.fig)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.data = []
        self.serial_port = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.read_serial_data)
        self.timer.start(100)  # Adjust the interval as needed

    def initUI(self):
        self.setWindowTitle("BLE Device Connector")
        self.showFullScreen()  # Set window to full screen

        # Set background color of the main window
        self.setStyleSheet("background-color: black;")

        self.canvas = MplCanvas(self, width=8, height=6, dpi=100)  # Increase plot size
        self.canvas.setStyleSheet("background-color: black;")

        self.connect_button = QPushButton('Connect', self)
        self.connect_button.setStyleSheet("background-color: black; color: white;")
        self.connect_button.clicked.connect(self.toggle_connection)

        self.close_button = QPushButton('Close', self)
        self.close_button.setStyleSheet("background-color: black; color: white;")
        self.close_button.clicked.connect(self.close_window)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.connect_button)
        button_layout.addWidget(self.close_button)
        button_layout.setContentsMargins(32, 32, 32, 32)  # Adjust margins to move components inward by 32 pixels

        layout = QVBoxLayout()
        layout.addWidget(self.canvas, stretch=1)  # Ensure the canvas takes most space
        layout.addLayout(button_layout)
        layout.setContentsMargins(0, 0,0,0)  # Ensure no margins around the main layout
        self.setLayout(layout)

    def toggle_connection(self):
        if self.serial_port and self.serial_port.is_open:
            self.disconnect_device()
        else:
            self.start_plotting()

    def start_plotting(self):
        self.connect_button.setDisabled(True)
        self.connect_button.setText("Connecting...")
        threading.Thread(target=self.connect_and_plot).start()

    def connect_and_plot(self):
        try:
            # Connect to the serial port
            self.serial_port = serial.Serial('/dev/ttyACM0', 115200, timeout=1)  # Adjust the port as needed
            self.connect_button.setEnabled(True)
            self.connect_button.setText("Disconnect")
        except Exception as e:
            print("An error occurred: {}".format(e))
            self.connect_button.setEnabled(True)
            self.connect_button.setText("Connect")

    def read_serial_data(self):
        if self.serial_port and self.serial_port.is_open:
            try:
                line = self.serial_port.readline().decode('utf-8').strip()
                if line:
                    print(f"Received: {line}")
                    values = line.split(',')
                    for value in values:
                        self.update_plot(float(value))
            except Exception as e:
                print(f"Failed to read from serial port: {e}")

    def update_plot(self, value):
        self.data.append(value)
        if len(self.data) > 100:  # Limit the number of points to display
            self.data.pop(0)
        self.canvas.ax.clear()
        self.canvas.ax.set_facecolor('black')  # Ensure background stays black
        self.canvas.ax.plot(self.data, 'r-')
        self.canvas.draw()

    def disconnect_device(self):
        try:
            if self.serial_port and self.serial_port.is_open:
                self.serial_port.close()
                print("Disconnected from serial port.")
        except Exception as e:
            print("An error occurred while disconnecting: {}".format(e))
        finally:
            self.serial_port = None
            self.connect_button.setText("Connect")

    def close_window(self):
        self.disconnect_device()
        self.close()


