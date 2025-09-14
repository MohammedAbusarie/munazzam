# munazzam/app/main_window.py

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
    QStackedWidget, QFrame, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt
# We need to import the pages from their new, correct locations
from .ui.cars_page import CarsPage
from .ui.pages import DashboardPage, EquipmentPage, OtherTablesPage

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Munazzam - نظام إدارة المخزون")
        self.setGeometry(100, 100, 1400, 800)
        
        # This will hold our navigation buttons to manage their styles
        self.nav_buttons = []

        self.setup_ui()
        self.setup_pages()
        self.connect_signals()

        # Set Initial State: Clicks the dashboard button to make it active on startup
        self.btnDashboard.click()

    def setup_ui(self):
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0); main_layout.setSpacing(0)
        self.setCentralWidget(central_widget)

        nav_bar_widget = QFrame()
        nav_bar_widget.setObjectName("navBar") 
        nav_bar_widget.setFixedWidth(220)
        
        nav_layout = QVBoxLayout(nav_bar_widget)
        nav_layout.setContentsMargins(10, 10, 10, 10); nav_layout.setSpacing(15)
        nav_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Create buttons and add them to our tracking list
        self.btnDashboard = self.create_nav_button("لوحة التحكم")
        self.btnCars = self.create_nav_button("السيارات")
        self.btnEquipment = self.create_nav_button("المعدات")
        self.btnOtherTables = self.create_nav_button("إدارة الجداول")
        
        self.nav_buttons.extend([self.btnDashboard, self.btnCars, self.btnEquipment, self.btnOtherTables])

        nav_layout.addWidget(self.btnDashboard)
        nav_layout.addWidget(self.btnCars)
        nav_layout.addWidget(self.btnEquipment)
        nav_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        nav_layout.addWidget(self.btnOtherTables)

        self.mainStackedWidget = QStackedWidget()
        main_layout.addWidget(nav_bar_widget)
        main_layout.addWidget(self.mainStackedWidget)

    def create_nav_button(self, text):
        button = QPushButton(text)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        return button

    def setup_pages(self):
        self.dashboard_page = DashboardPage()
        self.cars_page = CarsPage()
        self.equipment_page = EquipmentPage()
        self.other_tables_page = OtherTablesPage()
        
        self.mainStackedWidget.addWidget(self.dashboard_page)
        self.mainStackedWidget.addWidget(self.cars_page)
        self.mainStackedWidget.addWidget(self.equipment_page)
        self.mainStackedWidget.addWidget(self.other_tables_page)

    def connect_signals(self):
        """Connects each button to a central handler."""
        self.btnDashboard.clicked.connect(lambda: self.on_nav_button_clicked(self.btnDashboard, self.dashboard_page))
        self.btnCars.clicked.connect(lambda: self.on_nav_button_clicked(self.btnCars, self.cars_page))
        self.btnEquipment.clicked.connect(lambda: self.on_nav_button_clicked(self.btnEquipment, self.equipment_page))
        self.btnOtherTables.clicked.connect(lambda: self.on_nav_button_clicked(self.btnOtherTables, self.other_tables_page))

    def on_nav_button_clicked(self, clicked_button, target_page):
        """
        Switches the page and updates the style of all navigation buttons.
        """
        # Switch to the correct page
        self.mainStackedWidget.setCurrentWidget(target_page)

        # Update the 'active' property on all buttons
        for button in self.nav_buttons:
            is_active = (button == clicked_button)
            button.setProperty("active", is_active)
            
            # Force Qt to re-evaluate the stylesheet for this widget
            button.style().unpolish(button)
            button.style().polish(button)