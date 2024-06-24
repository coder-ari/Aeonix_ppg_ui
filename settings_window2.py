from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QStackedWidget, QLabel, QLineEdit, QComboBox, QMessageBox, QListWidgetItem
from PyQt5.QtCore import pyqtSignal, Qt, QSize, QLocale
import datetime
from PyQt5.QtGui import QIcon


class GeneralSettingsWidget(QWidget):
    dateChanged = pyqtSignal(datetime.date)
    timeChanged = pyqtSignal(datetime.time)
    locationChanged = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self.setStyleSheet("background-color: black; color: white;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)  # Add padding of 20px from all sides

        location_label = QLabel("Location:")
        location_label.setStyleSheet("font-size: 16px;")
        layout.addWidget(location_label)

        self.location_entry = QLineEdit()
        self.location_entry.setStyleSheet("font-size: 16px; border: 1px solid #808080; border-radius: 5px; padding: 5px;")
        layout.addWidget(self.location_entry)

        save_button = QPushButton("Save Location")
        save_button.setStyleSheet("font-size: 16px;")
        save_button.clicked.connect(self.save_location)
        layout.addWidget(save_button)

        time_label = QLabel("Set Time:")
        time_label.setStyleSheet("font-size: 16px;")
        layout.addWidget(time_label)

        time_layout = QHBoxLayout()
        layout.addLayout(time_layout)

        self.hour_combo = QComboBox()
        self.hour_combo.setStyleSheet("font-size: 16px;")
        self.hour_combo.addItems([f"{i:02d}" for i in range(24)])
        time_layout.addWidget(self.hour_combo)

        self.minute_combo = QComboBox()
        self.minute_combo.setStyleSheet("font-size: 16px;")
        self.minute_combo.addItems([f"{i:02d}" for i in range(60)])
        time_layout.addWidget(self.minute_combo)

        self.second_combo = QComboBox()
        self.second_combo.setStyleSheet("font-size: 16px;")
        self.second_combo.addItems([f"{i:02d}" for i in range(60)])
        time_layout.addWidget(self.second_combo)

        set_time_button = QPushButton("Set Time")
        set_time_button.setStyleSheet("font-size: 16px;")
        set_time_button.clicked.connect(self.set_time)
        layout.addWidget(set_time_button)

        date_label = QLabel("Set Date:")
        date_label.setStyleSheet("font-size: 16px;")
        layout.addWidget(date_label)

        date_layout = QHBoxLayout()
        layout.addLayout(date_layout)

        self.day_combo = QComboBox()
        self.day_combo.setStyleSheet("font-size: 16px;")
        self.day_combo.addItems([f"{i:02d}" for i in range(1, 32)])
        date_layout.addWidget(self.day_combo)

        self.month_combo = QComboBox()
        self.month_combo.setStyleSheet("font-size: 16px;")
        self.month_combo.addItems([f"{i:02d}" for i in range(1, 13)])
        date_layout.addWidget(self.month_combo)

        self.year_combo = QComboBox()
        self.year_combo.setStyleSheet("font-size: 16px;")
        self.year_combo.addItems([str(i) for i in range(2000, 2101)])
        date_layout.addWidget(self.year_combo)

        set_date_button = QPushButton("Set Date")
        set_date_button.setStyleSheet("font-size: 16px;")
        set_date_button.clicked.connect(self.set_date)
        layout.addWidget(set_date_button)

    def save_location(self):
        new_location = self.location_entry.text()
        self.locationChanged.emit(new_location)
        QMessageBox.information(self, "Settings Saved", f"New location saved: {new_location}")

    def set_time(self):
        hours = self.hour_combo.currentText()
        minutes = self.minute_combo.currentText()
        seconds = self.second_combo.currentText()
        new_time = datetime.time(int(hours), int(minutes), int(seconds))
        self.timeChanged.emit(new_time)
        QMessageBox.information(self, "Time Set", f"New time set: {new_time}")

    def set_date(self):
        day = self.day_combo.currentText()
        month = self.month_combo.currentText()
        year = self.year_combo.currentText()
        new_date = datetime.date(int(year), int(month), int(day))
        
        # Set locale to English explicitly
        locale = QLocale(QLocale.English)
        weekday_name = locale.toString(new_date, 'dddd')  # Get localized day name
        self.weekday_label = QLabel()
        self.weekday_label.setText(f"{year}-{month}-{day} ({weekday_name})")
        self.weekday_label.setStyleSheet("font-size: 16px;")

        self.dateChanged.emit(new_date)
        QMessageBox.information(self, "Date Set", f"New date set: {new_date} ({weekday_name})")


class PPGSettingsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: black; color: white;")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("PPG Settings (to be implemented)"))

class SettingsWindow(QMainWindow):
    dateChanged = pyqtSignal(datetime.date)
    timeChanged = pyqtSignal(datetime.time)
    locationChanged = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Settings")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("background-color: black; color: white;")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("font-size: 32px; background-color: #000000; color: white; border: none; padding:20px")
        self.list_widget.setIconSize(QSize(32, 32))  # Set icon size
        self.list_widget.setMaximumWidth(600)  # Set fixed width for now
        main_layout.addWidget(self.list_widget)

        self.stacked_widget = QStackedWidget()
        self.general_settings = GeneralSettingsWidget()
        self.ppg_settings = PPGSettingsWidget()

        self.stacked_widget.addWidget(self.general_settings)
        self.stacked_widget.addWidget(self.ppg_settings)
        main_layout.addWidget(self.stacked_widget)

        # Add items to the list widget with icons
        general_item = QListWidgetItem("General Settings")
        general_item.setIcon(QIcon('general_icon.png'))
        general_item.setSizeHint(QSize(general_item.sizeHint().width(), 65))  # Set item height
        self.list_widget.addItem(general_item)

        ppg_item = QListWidgetItem("PPG Settings")
        ppg_item.setIcon(QIcon('ppg_icon.png'))
        ppg_item.setSizeHint(QSize(ppg_item.sizeHint().width(), 65))  # Set item height
        self.list_widget.addItem(ppg_item)

        self.list_widget.setSpacing(10)  # Set space between items

        self.list_widget.currentRowChanged.connect(self.display_settings)

        close_button = QPushButton("Close", self)
        close_button.setStyleSheet("font-size: 16px;")
        close_button.clicked.connect(self.close)
        main_layout.addWidget(close_button, alignment=Qt.AlignBottom)

        # Connect signals to methods that will emit to the main application
        self.general_settings.dateChanged.connect(self.emit_date_changed)
        self.general_settings.timeChanged.connect(self.emit_time_changed)
        self.general_settings.locationChanged.connect(self.emit_location_changed)

    def display_settings(self, index):
        self.stacked_widget.setCurrentIndex(index)

    def emit_date_changed(self, new_date):
        self.dateChanged.emit(new_date)

    def emit_time_changed(self, new_time):
        self.timeChanged.emit(new_time)

    def emit_location_changed(self, new_location):
        self.locationChanged.emit(new_location)

    def closeEvent(self, event):
        event.accept()

    def showEvent(self, event):
        super().showEvent(event)
        # Connect the signals to the parent clock methods
        if hasattr(self.parent(), 'clock'):
            self.dateChanged.connect(self.parent().clock.set_date)
            self.timeChanged.connect(self.parent().clock.set_time)
            self.locationChanged.connect(self.parent().clock.set_location)

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    app.setLocale(QLocale(QLocale.English))
    window = SettingsWindow()
    window.show()
    sys.exit(app.exec_())
