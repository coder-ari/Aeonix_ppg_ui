import sys
from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QApplication
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import threading
import time
from bluepy.btle import Scanner, Peripheral, UUID, DefaultDelegate, BTLEException
import json
import os
from settings_window2 import PPGSettingsWidget

class NotificationDelegate(DefaultDelegate):
    def __init__(self, parent):
        DefaultDelegate.__init__(self)
        self.parent = parent

    def handleNotification(self, cHandle, data):
        decoded_data = data.decode('utf-8')
        print("Notification from handle {}: {}".format(cHandle,decoded_data))
        self.parent.update_plot(float(decoded_data))

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
        self.peripheral = None
        self.data = []
        self.json_data_to_send = {
            "SamplingRate": 1000,
            "Brightness": 30,
            "SampleAverage": 1,
            "LedMode": 1,
            "PulseWidth": 411,
            "AdcRange": 16384
        }

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
        layout.setContentsMargins(32, 32, 32, 32)  # Ensure no margins around the main layout
        self.setLayout(layout)

    def toggle_connection(self):
        if self.peripheral:
            self.disconnect_device()
        else:
            self.start_plotting()

    def start_plotting(self):
        self.connect_button.setDisabled(True)
        self.connect_button.setText("Connecting...")
        threading.Thread(target=self.connect_and_plot).start()

    def connect_and_plot(self):
        try:
            json_data_to_send = self.json_data_to_send  # Initialize with current settings

            DEVICE_ADDRESS = "30:30:f9:18:19:09"  
            SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E" 
            WRITE_CHAR_UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"  
            READ_CHAR_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"

            print("Scanning for devices...")
            devices = scan_for_devices()
            
            if not any(dev.addr == DEVICE_ADDRESS for dev in devices):
                raise Exception("Device with address {} not found during scan.".format(DEVICE_ADDRESS))
            
            self.peripheral, write_char, read_char = connect_to_device(DEVICE_ADDRESS, SERVICE_UUID, WRITE_CHAR_UUID, READ_CHAR_UUID, self)
            write_json_to_characteristic(write_char, json_data_to_send)
            enable_notifications(self.peripheral, read_char)
            self.read_and_plot_from_characteristic()
        except Exception as e:
            print("An error occurred: {}".format(e))
            self.connect_button.setEnabled(True)
            self.connect_button.setText("Connect")

    def read_and_plot_from_characteristic(self):
        self.connect_button.setEnabled(True)
        self.connect_button.setText("Disconnect")
        while self.peripheral:
            if self.peripheral.waitForNotifications(1.0):
                continue
            time.sleep(1)

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
            if self.peripheral:
                self.peripheral.disconnect()
                print("Disconnected from device.")
        except Exception as e:
            print("An error occurred while disconnecting: {}".format(e))
        finally:
            self.peripheral = None
            self.connect_button.setText("Connect")

    def update_sampling_rate(self, value):
        self.json_data_to_send["SamplingRate"] = value

    def update_brightness(self, value):
        self.json_data_to_send["Brightness"] = value

    def update_sample_average(self, value):
        self.json_data_to_send["SampleAverage"] = value

    def update_led_mode(self, value):
        self.json_data_to_send["LedMode"] = value

    def update_pulse_width(self, value):
        self.json_data_to_send["PulseWidth"] = value

    def update_adc_range(self, value):
        self.json_data_to_send["AdcRange"] = value

    def close_window(self):
        self.disconnect_device()
        self.close()

def connect_to_device(device_address, service_uuid, write_char_uuid, read_char_uuid, parent):
    print("Connecting to device with address: {}".format(device_address))
    peripheral = Peripheral(device_address)
    peripheral.setDelegate(NotificationDelegate(parent))

    # Get service
    service = peripheral.getServiceByUUID(UUID(service_uuid))
    if not service:
        raise Exception("Service with UUID {} not found.".format(service_uuid))

    # Get characteristics
    write_char = service.getCharacteristics(UUID(write_char_uuid))
    if not write_char:
        raise Exception("Write characteristic with UUID {} not found.".format(write_char_uuid))
    write_char = write_char[0]

    read_char = service.getCharacteristics(UUID(read_char_uuid))
    if not read_char:
        raise Exception("Read characteristic with UUID {} not found.".format(read_char_uuid))
    read_char = read_char[0]

    return peripheral, write_char, read_char

def write_json_to_characteristic(characteristic, data):
    json_data = json.dumps(data)
    characteristic.write(json_data.encode('utf-8'), withResponse=True)
    print("Successfully written data to characteristic: {}".format(json_data))

def enable_notifications(peripheral, characteristic):
    try:
        cccid = characteristic.getHandle() + 1
        peripheral.writeCharacteristic(cccid, b'\x01\x00', True)
        print("Enabled notifications for characteristic: {}".format(characteristic.uuid))
    except BTLEException as e:
        print("Failed to enable notifications: {}".format(e))

def scan_for_devices():
    scanner = Scanner()
    devices = scanner.scan(10.0)
    for dev in devices:
        print("Device {} ({}), RSSI={} dB".format(dev.addr,dev.addrType,dev.rssi))
        for (adtype, desc, value) in dev.getScanData():
            print("  {} = {}".format(desc,value))
    return devices
    