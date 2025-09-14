# munazzam/app/ui/pages.py

from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt

class BasePage(QWidget):
    """A simple base class for our pages to reduce boilerplate."""
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setObjectName(f"{title.replace(' ', '_')}Page")
        
        layout = QVBoxLayout(self)
        label = QLabel(title)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("font-size: 24pt; font-weight: bold; color: #7F8C8D;")
        layout.addWidget(label)
        self.setLayout(layout)

# --- Create specific page classes ---

class DashboardPage(BasePage):
    def __init__(self, parent=None):
        super().__init__("Dashboard Page (To Be Implemented)", parent)
        # Add card widgets here in the future

class CarsPage(BasePage):
    def __init__(self, parent=None):
        super().__init__("Cars CRUD Page", parent)
        # Add table view, search, and action buttons here

class EquipmentPage(BasePage):
    def __init__(self, parent=None):
        super().__init__("Equipment CRUD Page", parent)
        # Add table view, search, and action buttons here

class OtherTablesPage(BasePage):
    def __init__(self, parent=None):
        super().__init__("Generic Table Management", parent)
        # Add a QComboBox to select the table and a QTableView here