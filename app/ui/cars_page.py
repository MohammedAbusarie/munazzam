# munazzam/app/ui/cars_page.py

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QHeaderView, QLabel, QGroupBox, QLineEdit, QRadioButton, QButtonGroup
)
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QPixmap
from .workers import DatabaseWorker
from .dialogs.car_form_dialog import CarFormDialog
import os

class CarsPage(QWidget):
    request_load_cars = pyqtSignal()
    request_load_lookup_data = pyqtSignal()
    request_add_car = pyqtSignal(dict)
    request_update_car = pyqtSignal(int, dict)
    request_delete_car = pyqtSignal(int)

    # --- Define searchable columns for the radio buttons ---
    # Maps the Arabic label to the SQLAlchemy model attribute name
    SEARCH_COLUMNS = {
        "رقم الأسطول": "fleet_no",
        "لوحة (EN)": "plate_no_en",
        "لوحة (AR)": "plate_no_ar",
        "المصنع": "manufacturer.name"
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.lookup_data = {}
        self.current_car_id = None
        self.all_cars = []  # This will store the full, unfiltered list of cars
        self.placeholder_image_path = self.find_placeholder_image()
        
        self.setup_ui()
        self.setup_worker_thread()
        self.load_initial_data()

    def find_placeholder_image(self):
        path = os.path.join("app", "assets", "placeholder.png")
        return path if os.path.exists(path) else None

    def setup_ui(self):
        main_layout = QVBoxLayout(self)

        # --- Top Action Buttons ---
        top_buttons_layout = QHBoxLayout()
        self.add_btn = QPushButton("إضافة سيارة جديدة"); self.update_btn = QPushButton("تعديل المحدد"); self.delete_btn = QPushButton("حذف المحدد")
        self.add_btn.setObjectName("primaryButton"); self.update_btn.setEnabled(False); self.delete_btn.setEnabled(False)
        top_buttons_layout.addWidget(self.add_btn); top_buttons_layout.addWidget(self.update_btn); top_buttons_layout.addWidget(self.delete_btn); top_buttons_layout.addStretch()

        # --- Search Panel ---
        search_group = QGroupBox("بحث")
        search_layout = QHBoxLayout(search_group)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("ادخل نص البحث...")
        search_layout.addWidget(self.search_input, 1) # Give search input more space

        self.search_criteria_group = QButtonGroup(self)
        for i, text in enumerate(self.SEARCH_COLUMNS.keys()):
            radio_button = QRadioButton(text)
            search_layout.addWidget(radio_button)
            self.search_criteria_group.addButton(radio_button, i)
            if i == 0:  # Set the first radio button as the default
                radio_button.setChecked(True)
        
        # --- Table ---
        self.cars_table = QTableWidget()
        self.cars_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.cars_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers) # Make table read-only
        self.cars_table.setAlternatingRowColors(True)
        # --- THIS ENABLES SORTING ---
        self.cars_table.setSortingEnabled(True)

        # Add all widgets to the main layout
        main_layout.addLayout(top_buttons_layout)
        main_layout.addWidget(search_group)
        main_layout.addWidget(self.cars_table)
        
        # --- Connect Signals ---
        self.cars_table.selectionModel().selectionChanged.connect(self.on_table_selection_changed)
        self.add_btn.clicked.connect(self.open_add_dialog)
        self.update_btn.clicked.connect(self.open_update_dialog)
        self.delete_btn.clicked.connect(self.handle_delete)
        # Connect search signals to the filtering slot
        self.search_input.textChanged.connect(self.filter_table)
        self.search_criteria_group.buttonClicked.connect(self.filter_table)

    def setup_worker_thread(self):
        self.worker_thread = QThread(); self.db_worker = DatabaseWorker(); self.db_worker.moveToThread(self.worker_thread)
        self.db_worker.cars_loaded.connect(self.on_cars_loaded) # Connect to the new handler
        self.db_worker.lookup_data_loaded.connect(self.on_lookup_data_loaded)
        self.db_worker.operation_successful.connect(self.on_operation_success)
        self.db_worker.operation_failed.connect(self.on_operation_failure)
        self.request_load_cars.connect(self.db_worker.load_cars)
        self.request_load_lookup_data.connect(self.db_worker.load_lookup_data)
        self.request_add_car.connect(self.db_worker.add_car)
        self.request_update_car.connect(self.db_worker.update_car)
        self.request_delete_car.connect(self.db_worker.delete_car)
        self.worker_thread.start()

    def load_initial_data(self):
        self.request_load_lookup_data.emit()
        self.request_load_cars.emit()
        
    def on_lookup_data_loaded(self, data):
        self.lookup_data = data

    def on_cars_loaded(self, cars):
        """
        Receives the full list of cars from the worker, stores it,
        and triggers the initial population of the table.
        """
        self.all_cars = cars
        self.filter_table() # Populate the table with the full, unfiltered list

    def filter_table(self):
        """
        Filters the `self.all_cars` list based on the search criteria
        and then calls the method to populate the table with the results.
        """
        search_text = self.search_input.text().strip().lower()
        checked_button = self.search_criteria_group.checkedButton()
        
        if not checked_button:
            self.populate_table(self.all_cars)
            return

        search_column_key = checked_button.text()
        attribute_name = self.SEARCH_COLUMNS[search_column_key]

        if not search_text:
            self.populate_table(self.all_cars)
            return

        filtered_cars = []
        for car in self.all_cars:
            if '.' in attribute_name: # Handle related object attributes like 'manufacturer.name'
                parts = attribute_name.split('.')
                value_obj = getattr(car, parts[0], None)
                value = getattr(value_obj, parts[1], "") if value_obj else ""
            else:
                value = getattr(car, attribute_name, "")
            
            if search_text in str(value).lower():
                filtered_cars.append(car)
        
        self.populate_table(filtered_cars)

    def populate_table(self, cars):
        """
        The main method to populate the QTableWidget with a given list of cars.
        This now handles all table drawing.
        """
        self.cars_table.setSortingEnabled(False) # Disable sorting during population for performance
        
        headers = [
            "الصورة", "رقم الأسطول", "لوحة (EN)", "لوحة (AR)", "الإدارة (Code)", "الفئة",
            "المصنع", "الموديل", "الموقع الوظيفي", "الملكية", "الغرفة", "وصف الموقع",
            "تفاصيل العنوان", "مستلم الإشعار", "العقد", "الإدارة (Mgmt)", "النشاط",
            "بداية الترخيص", "نهاية الترخيص", "بداية الفحص", "نهاية الفحص", "ID"
        ]
        self.cars_table.setColumnCount(len(headers)); self.cars_table.setHorizontalHeaderLabels(headers)
        self.cars_table.setRowCount(0); self.cars_table.verticalHeader().setDefaultSectionSize(80)
        
        def safe_get(obj, attr_path, default=""):
            try:
                temp = obj
                for part in attr_path.split('.'):
                    temp = getattr(temp, part)
                return str(temp) if temp is not None else default
            except AttributeError:
                return default

        for row, car in enumerate(cars):
            self.cars_table.insertRow(row)
            
            # Image Column
            if self.placeholder_image_path:
                pixmap = QPixmap(self.placeholder_image_path)
                if not pixmap.isNull():
                    label = QLabel(); label.setPixmap(pixmap.scaled(100, 75, Qt.AspectRatioMode.KeepAspectRatio)); label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.cars_table.setCellWidget(row, 0, label)

            # Data Columns
            self.cars_table.setItem(row, 1, QTableWidgetItem(car.fleet_no))
            self.cars_table.setItem(row, 2, QTableWidgetItem(car.plate_no_en))
            self.cars_table.setItem(row, 3, QTableWidgetItem(car.plate_no_ar))
            self.cars_table.setItem(row, 4, QTableWidgetItem(safe_get(car, 'department.name')))
            self.cars_table.setItem(row, 5, QTableWidgetItem(safe_get(car, 'car_class.name')))
            self.cars_table.setItem(row, 6, QTableWidgetItem(safe_get(car, 'manufacturer.name')))
            self.cars_table.setItem(row, 7, QTableWidgetItem(safe_get(car, 'model.name')))
            self.cars_table.setItem(row, 8, QTableWidgetItem(safe_get(car, 'functional_location.name')))
            self.cars_table.setItem(row, 9, QTableWidgetItem(safe_get(car, 'ownership.value')))
            self.cars_table.setItem(row, 10, QTableWidgetItem(safe_get(car, 'room_type.value')))
            self.cars_table.setItem(row, 11, QTableWidgetItem(safe_get(car, 'location_description.name')))
            self.cars_table.setItem(row, 12, QTableWidgetItem(car.address_details_1))
            self.cars_table.setItem(row, 13, QTableWidgetItem(safe_get(car, 'notification_recipient.name')))
            self.cars_table.setItem(row, 14, QTableWidgetItem(safe_get(car, 'contract_type.name')))
            self.cars_table.setItem(row, 15, QTableWidgetItem(safe_get(car, 'management.name')))
            self.cars_table.setItem(row, 16, QTableWidgetItem(safe_get(car, 'activity.name')))
            self.cars_table.setItem(row, 17, QTableWidgetItem(safe_get(car, 'registration_start_date')))
            self.cars_table.setItem(row, 18, QTableWidgetItem(safe_get(car, 'registration_end_date')))
            self.cars_table.setItem(row, 19, QTableWidgetItem(safe_get(car, 'inspection_start_date')))
            self.cars_table.setItem(row, 20, QTableWidgetItem(safe_get(car, 'inspection_end_date')))
            self.cars_table.setItem(row, 21, QTableWidgetItem(str(car.id)))
            
            self.cars_table.item(row, 21).setData(100, car)

        self.cars_table.resizeColumnsToContents()
        self.cars_table.setSortingEnabled(True) # Re-enable sorting after population

    def on_table_selection_changed(self):
        has_selection = bool(self.cars_table.selectedItems())
        self.update_btn.setEnabled(has_selection); self.delete_btn.setEnabled(has_selection)
        if has_selection:
            selected_row = self.cars_table.selectedItems()[0].row()
            id_column = self.cars_table.columnCount() - 1
            self.current_car_id = int(self.cars_table.item(selected_row, id_column).text())

    def open_add_dialog(self):
        dialog = CarFormDialog(self.lookup_data, self)
        if dialog.exec():
            self.request_add_car.emit(dialog.get_data())

    def open_update_dialog(self):
        if not self.cars_table.selectedItems(): return
        selected_row = self.cars_table.selectedItems()[0].row()
        id_column = self.cars_table.columnCount() - 1
        car_to_edit = self.cars_table.item(selected_row, id_column).data(100)
        
        dialog = CarFormDialog(self.lookup_data, self); dialog.set_data(car_to_edit)
        if dialog.exec():
            self.request_update_car.emit(car_to_edit.id, dialog.get_data())

    def handle_delete(self):
        if not self.current_car_id: return
        reply = QMessageBox.warning(self, "تأكيد الحذف", "هل أنت متأكد أنك تريد حذف هذه السيارة؟",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.request_delete_car.emit(self.current_car_id)

    def on_operation_success(self, message):
        QMessageBox.information(self, "نجاح", message); self.request_load_cars.emit()

    def on_operation_failure(self, message):
        QMessageBox.critical(self, "خطأ", message)
        
    def closeEvent(self, event):
        self.worker_thread.quit(); self.worker_thread.wait(); super().closeEvent(event)