# munazzam/app/ui/cars_page.py

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QHeaderView, QLabel
)
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QPixmap
from .workers import DatabaseWorker
from .dialogs.car_form_dialog import CarFormDialog
import os # To find a placeholder image

class CarsPage(QWidget):
    request_load_cars = pyqtSignal()
    request_load_lookup_data = pyqtSignal()
    request_add_car = pyqtSignal(dict)
    request_update_car = pyqtSignal(int, dict)
    request_delete_car = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.lookup_data = {}
        self.current_car_id = None
        # --- Find a placeholder image for the table ---
        # In a real app, you would package an image file. We will try to find one.
        self.placeholder_image_path = self.find_placeholder_image()
        
        self.setup_ui()
        self.setup_worker_thread()
        self.load_initial_data()

    def find_placeholder_image(self):
        # This is a dummy function. Create a 'placeholder.png' in app/assets for it to work.
        # Otherwise, no image will show in the table.
        path = os.path.join("app", "assets", "placeholder.png")
        return path if os.path.exists(path) else None

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        buttons_layout = QHBoxLayout()
        self.add_btn = QPushButton("إضافة سيارة جديدة"); self.update_btn = QPushButton("تعديل المحدد"); self.delete_btn = QPushButton("حذف المحدد")
        self.add_btn.setObjectName("primaryButton"); self.update_btn.setEnabled(False); self.delete_btn.setEnabled(False)
        buttons_layout.addWidget(self.add_btn); buttons_layout.addWidget(self.update_btn); buttons_layout.addWidget(self.delete_btn); buttons_layout.addStretch()
        
        self.cars_table = QTableWidget()
        self.cars_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.cars_table.selectionModel().selectionChanged.connect(self.on_table_selection_changed)
        
        main_layout.addLayout(buttons_layout); main_layout.addWidget(self.cars_table)
        
        self.add_btn.clicked.connect(self.open_add_dialog)
        self.update_btn.clicked.connect(self.open_update_dialog)
        self.delete_btn.clicked.connect(self.handle_delete)

    def setup_worker_thread(self):
        self.worker_thread = QThread(); self.db_worker = DatabaseWorker(); self.db_worker.moveToThread(self.worker_thread)
        self.db_worker.cars_loaded.connect(self.populate_cars_table)
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

    def populate_cars_table(self, cars):
        headers = [
            "الصورة", "رقم الأسطول", "لوحة (EN)", "لوحة (AR)", "الإدارة (Code)", "الفئة",
            "المصنع", "الموديل", "الموقع الوظيفي", "الملكية", "الغرفة", "وصف الموقع",
            "تفاصيل العنوان", "مستلم الإشعار", "العقد", "الإدارة (Mgmt)", "النشاط",
            "بداية الترخيص", "نهاية الترخيص", "بداية الفحص", "نهاية الفحص", "ID"
        ]
        self.cars_table.setColumnCount(len(headers)); self.cars_table.setHorizontalHeaderLabels(headers)
        self.cars_table.setRowCount(0); self.cars_table.verticalHeader().setDefaultSectionSize(80)
        
        def safe_get(obj, attr, default=""):
            rel_obj = getattr(obj, attr.split('.')[0], None)
            return getattr(rel_obj, attr.split('.')[1], default) if '.' in attr and rel_obj else (getattr(obj, attr, default) or default)

        for row, car in enumerate(cars):
            self.cars_table.insertRow(row)
            
            # --- Image Column ---
            if self.placeholder_image_path:
                pixmap = QPixmap(self.placeholder_image_path)
                if not pixmap.isNull():
                    label = QLabel(); label.setPixmap(pixmap.scaled(100, 75, Qt.AspectRatioMode.KeepAspectRatio)); label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.cars_table.setCellWidget(row, 0, label)

            # --- Data Columns ---
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
            self.cars_table.setItem(row, 17, QTableWidgetItem(str(car.registration_start_date or '')))
            self.cars_table.setItem(row, 18, QTableWidgetItem(str(car.registration_end_date or '')))
            self.cars_table.setItem(row, 19, QTableWidgetItem(str(car.inspection_start_date or '')))
            self.cars_table.setItem(row, 20, QTableWidgetItem(str(car.inspection_end_date or '')))
            self.cars_table.setItem(row, 21, QTableWidgetItem(str(car.id)))
            
            self.cars_table.item(row, 21).setData(100, car)

        self.cars_table.resizeColumnsToContents()

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