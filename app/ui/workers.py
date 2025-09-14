# munazzam/app/ui/workers.py

from PyQt6.QtCore import QObject, pyqtSignal
from app.core import inventory_management as im

class DatabaseWorker(QObject):
    """
    A worker that performs database operations on a separate thread.
    """
    # --- Signals to send results back to the UI ---
    cars_loaded = pyqtSignal(list)
    lookup_data_loaded = pyqtSignal(dict)
    operation_successful = pyqtSignal(str)
    operation_failed = pyqtSignal(str)

    # --- Slots to receive requests from the UI ---
    def load_cars(self):
        try:
            cars = im.get_all_cars_with_details()
            self.cars_loaded.emit(cars)
        except Exception as e:
            self.operation_failed.emit(f"Failed to load cars: {e}")
    
    def load_lookup_data(self):
        try:
            data = im.get_lookup_data()
            self.lookup_data_loaded.emit(data)
        except Exception as e:
            self.operation_failed.emit(f"Failed to load form data: {e}")

    def add_car(self, car_data):
        result = im.add_car(car_data)
        if result["success"]:
            self.operation_successful.emit(result["message"])
        else:
            self.operation_failed.emit(result["message"])

    def update_car(self, car_id, car_data):
        result = im.update_car(car_id, car_data)
        if result["success"]:
            self.operation_successful.emit(result["message"])
        else:
            self.operation_failed.emit(result["message"])

    def delete_car(self, car_id):
        result = im.delete_car(car_id)
        if result["success"]:
            self.operation_successful.emit(result["message"])
        else:
            self.operation_failed.emit(result["message"])