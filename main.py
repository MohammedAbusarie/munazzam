# main.py

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from app.main_window import MainWindow

def run_application():
    app = QApplication(sys.argv)
    
    # --- CRITICAL FOR ARABIC UI ---
    # This sets the layout direction for the entire application to Right-to-Left.
    app.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
    
    # Load the stylesheet
    try:
        with open("app/assets/theme.qss", "r") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        print("Stylesheet not found. Please check the path.")

    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    run_application()