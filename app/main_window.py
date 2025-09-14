# munazzam/app/main_window.py

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
    QStackedWidget, QFrame, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt
from .ui.pages import DashboardPage, EquipmentPage, OtherTablesPage # Remove CarsPage
from .ui.cars_page import CarsPage # Add this new import


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # --- Window Properties ---
        self.setWindowTitle("Munazzam - نظام إدارة المخزون")
        self.setGeometry(100, 100, 1200, 700)
        
        # --- Setup UI Programmatically ---
        self.setup_ui()
        
        # --- Page Setup ---
        self.setup_pages()
        
        # --- Connect Signals to Slots ---
        self.connect_signals()

        # --- Set Initial State ---
        self.btnDashboard.click() # Start on the dashboard page

    def setup_ui(self):
        # Set layout direction for the entire window
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        
        # --- Main Layout ---
        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setCentralWidget(central_widget)

        # --- Navigation Bar (Right Side) ---
        nav_bar_widget = QFrame()
        nav_bar_widget.setObjectName("navBarWidget")
        nav_bar_widget.setFixedWidth(200)
        nav_bar_widget.setStyleSheet("#navBarWidget { background-color: #34495E; }")
        
        nav_layout = QVBoxLayout(nav_bar_widget)
        nav_layout.setContentsMargins(10, 10, 10, 10)
        nav_layout.setSpacing(15)
        nav_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # --- Navigation Buttons ---
        self.btnDashboard = self.create_nav_button("لوحة التحكم")
        self.btnCars = self.create_nav_button("السيارات")
        self.btnEquipment = self.create_nav_button("المعدات")
        self.btnOtherTables = self.create_nav_button("إدارة الجداول")
        
        nav_layout.addWidget(self.btnDashboard)
        nav_layout.addWidget(self.btnCars)
        nav_layout.addWidget(self.btnEquipment)
        nav_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        nav_layout.addWidget(self.btnOtherTables)

        # --- Main Content Area (Left Side) ---
        self.mainStackedWidget = QStackedWidget()
        
        # Add nav bar and content area to the main layout
        main_layout.addWidget(nav_bar_widget)
        main_layout.addWidget(self.mainStackedWidget)

    def create_nav_button(self, text):
        button = QPushButton(text)
        # Apply styling from your QSS file using object names or types
        # This is a simplified style, your theme.qss will handle the rest.
        button.setStyleSheet("color: white; font-size: 14pt; text-align: right; padding: 10px; border: none;")
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        return button

    def setup_pages(self):
        """Initializes and adds pages to the stacked widget."""
        self.dashboard_page = DashboardPage()
        self.cars_page = CarsPage()
        self.equipment_page = EquipmentPage()
        self.other_tables_page = OtherTablesPage()
        
        self.mainStackedWidget.addWidget(self.dashboard_page)
        self.mainStackedWidget.addWidget(self.cars_page)
        self.mainStackedWidget.addWidget(self.equipment_page)
        self.mainStackedWidget.addWidget(self.other_tables_page)

    def connect_signals(self):
        """Connects navigation button clicks to the page switching slot."""
        self.btnDashboard.clicked.connect(lambda: self.mainStackedWidget.setCurrentWidget(self.dashboard_page))
        self.btnCars.clicked.connect(lambda: self.mainStackedWidget.setCurrentWidget(self.cars_page))
        self.btnEquipment.clicked.connect(lambda: self.mainStackedWidget.setCurrentWidget(self.equipment_page))
        self.btnOtherTables.clicked.connect(lambda: self.mainStackedWidget.setCurrentWidget(self.other_tables_page))