# munazzam/app/ui/dialogs/car_form_dialog.py

from PyQt6.QtWidgets import (
    QDialog, QDialogButtonBox, QVBoxLayout, QGridLayout, QLabel, QLineEdit,
    QComboBox, QDateEdit, QRadioButton, QGroupBox, QPushButton, QTextEdit,
    QButtonGroup, QMessageBox, QFileDialog, QHBoxLayout
)
from PyQt6.QtCore import QDate, Qt
from PyQt6.QtGui import QPixmap
from app.core.models import OwnershipStatus, RoomType

class CarFormDialog(QDialog):
    def __init__(self, lookup_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("إضافة / تحديث سيارة")
        self.setMinimumSize(950, 700)
        self.lookup_data = lookup_data
        self.image_path = None

        self.setup_ui()
        self.populate_comboboxes()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        form_grid_layout = QGridLayout()

        # --- All Input Fields ---
        self.fleet_no_input = QLineEdit()
        self.plate_no_en_input = QLineEdit()
        self.plate_no_ar_input = QLineEdit()
        self.department_combo = QComboBox()
        self.carclass_combo = QComboBox()
        self.manufacturer_combo = QComboBox()
        self.model_combo = QComboBox()
        self.functionallocation_combo = QComboBox()
        self.locationdescription_combo = QComboBox()
        self.notificationrecipient_combo = QComboBox()
        self.contracttype_combo = QComboBox()
        self.management_combo = QComboBox()
        self.activity_combo = QComboBox()
        self.address_details_input = QTextEdit()
        
        self.registration_start_date = QDateEdit(calendarPopup=True)
        self.registration_end_date = QDateEdit(calendarPopup=True)
        self.inspection_start_date = QDateEdit(calendarPopup=True)
        self.inspection_end_date = QDateEdit(calendarPopup=True)
        for date_edit in [self.registration_start_date, self.registration_end_date, self.inspection_start_date, self.inspection_end_date]:
            date_edit.setDate(QDate.currentDate())
            date_edit.setDisplayFormat("yyyy-MM-dd")

        # --- Radio Button Groups ---
        ownership_group = QGroupBox("الملكية")
        ownership_layout = QHBoxLayout(ownership_group); self.owned_radio = QRadioButton("مملوكة"); self.leased_radio = QRadioButton("مستأجرة")
        self.ownership_group = QButtonGroup(self); self.ownership_group.addButton(self.owned_radio); self.ownership_group.addButton(self.leased_radio)
        ownership_layout.addWidget(self.owned_radio); ownership_layout.addWidget(self.leased_radio)

        room_group = QGroupBox("الغرفة")
        room_layout = QHBoxLayout(room_group); self.regular_radio = QRadioButton("عادي"); self.non_regular_radio = QRadioButton("غير عادي"); self.emp_24hrs_radio = QRadioButton("موظف 24 ساعة")
        self.room_group = QButtonGroup(self); self.room_group.addButton(self.regular_radio); self.room_group.addButton(self.non_regular_radio); self.room_group.addButton(self.emp_24hrs_radio)
        room_layout.addWidget(self.regular_radio); room_layout.addWidget(self.non_regular_radio); room_layout.addWidget(self.emp_24hrs_radio)

        # --- Image Upload Section ---
        image_group = QGroupBox("صورة السيارة")
        image_layout = QVBoxLayout(image_group); self.image_preview_label = QLabel("لم يتم تحديد صورة")
        self.image_preview_label.setMinimumSize(240, 180); self.image_preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_preview_label.setStyleSheet("border: 1px solid #BDC3C7;"); self.select_image_btn = QPushButton("اختر صورة")
        self.select_image_btn.clicked.connect(self._select_image); image_layout.addWidget(self.image_preview_label); image_layout.addWidget(self.select_image_btn)

        # --- Layout (3 Columns for data entry) ---
        # Column 0 & 1
        form_grid_layout.addWidget(QLabel("رقم الأسطول:"), 0, 0); form_grid_layout.addWidget(self.fleet_no_input, 0, 1)
        form_grid_layout.addWidget(QLabel("رقم اللوحة (EN):"), 1, 0); form_grid_layout.addWidget(self.plate_no_en_input, 1, 1)
        form_grid_layout.addWidget(QLabel("رقم اللوحة (AR):"), 2, 0); form_grid_layout.addWidget(self.plate_no_ar_input, 2, 1)
        form_grid_layout.addWidget(QLabel("الإدارة (Code):"), 3, 0); form_grid_layout.addWidget(self.department_combo, 3, 1)
        form_grid_layout.addWidget(QLabel("الفئة:"), 4, 0); form_grid_layout.addWidget(self.carclass_combo, 4, 1)
        form_grid_layout.addWidget(QLabel("المصنع:"), 5, 0); form_grid_layout.addWidget(self.manufacturer_combo, 5, 1)
        form_grid_layout.addWidget(QLabel("الموديل:"), 6, 0); form_grid_layout.addWidget(self.model_combo, 6, 1)
        form_grid_layout.addWidget(QLabel("الموقع الوظيفي:"), 7, 0); form_grid_layout.addWidget(self.functionallocation_combo, 7, 1)
        
        # Column 2 & 3
        form_grid_layout.addWidget(QLabel("وصف الموقع:"), 0, 2); form_grid_layout.addWidget(self.locationdescription_combo, 0, 3)
        form_grid_layout.addWidget(QLabel("مستلم الإشعار:"), 1, 2); form_grid_layout.addWidget(self.notificationrecipient_combo, 1, 3)
        form_grid_layout.addWidget(QLabel("العقد:"), 2, 2); form_grid_layout.addWidget(self.contracttype_combo, 2, 3)
        form_grid_layout.addWidget(QLabel("الإدارة (Mgmt):"), 3, 2); form_grid_layout.addWidget(self.management_combo, 3, 3)
        form_grid_layout.addWidget(QLabel("النشاط:"), 4, 2); form_grid_layout.addWidget(self.activity_combo, 4, 3)
        form_grid_layout.addWidget(ownership_group, 5, 2, 1, 2); form_grid_layout.addWidget(room_group, 6, 2, 1, 2)
        
        # Dates and Address spanning columns
        form_grid_layout.addWidget(QLabel("بداية الترخيص:"), 8, 0); form_grid_layout.addWidget(self.registration_start_date, 8, 1)
        form_grid_layout.addWidget(QLabel("نهاية الترخيص:"), 8, 2); form_grid_layout.addWidget(self.registration_end_date, 8, 3)
        form_grid_layout.addWidget(QLabel("بداية الفحص:"), 9, 0); form_grid_layout.addWidget(self.inspection_start_date, 9, 1)
        form_grid_layout.addWidget(QLabel("نهاية الفحص:"), 9, 2); form_grid_layout.addWidget(self.inspection_end_date, 9, 3)
        form_grid_layout.addWidget(QLabel("تفاصيل العنوان:"), 10, 0); form_grid_layout.addWidget(self.address_details_input, 10, 1, 1, 3)
        
        # Image in Column 4
        form_grid_layout.addWidget(image_group, 0, 4, 10, 1)
        form_grid_layout.setColumnStretch(1, 1); form_grid_layout.setColumnStretch(3, 1)

        # Dialog Buttons
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttonBox.accepted.connect(self.accept); 
        self.buttonBox.rejected.connect(self.reject);

        # --- ADD THESE TWO LINES TO TRANSLATE THE BUTTONS ---
        self.buttonBox.button(QDialogButtonBox.StandardButton.Ok).setText("موافق")
        self.buttonBox.button(QDialogButtonBox.StandardButton.Cancel).setText("إلغاء")
        
        main_layout.addLayout(form_grid_layout); main_layout.addWidget(self.buttonBox)

    def _select_image(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "اختر صورة", "", "Image Files (*.png *.jpg *.jpeg *.bmp)")
        if file_name:
            self.image_path = file_name
            pixmap = QPixmap(file_name)
            self.image_preview_label.setPixmap(pixmap.scaled(self.image_preview_label.size(), aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio))

    def populate_comboboxes(self):
        def _populate(combo, items):
            combo.addItem("اختر...", userData=None)
            if items:
                for item in items: combo.addItem(item.name, userData=item.id)
        
        _populate(self.department_combo, self.lookup_data.get('departments'))
        _populate(self.carclass_combo, self.lookup_data.get('car_classes'))
        _populate(self.manufacturer_combo, self.lookup_data.get('manufacturers'))
        _populate(self.model_combo, self.lookup_data.get('models'))
        _populate(self.functionallocation_combo, self.lookup_data.get('functional_locations'))
        _populate(self.locationdescription_combo, self.lookup_data.get('location_descriptions'))
        _populate(self.notificationrecipient_combo, self.lookup_data.get('notification_recipients'))
        _populate(self.contracttype_combo, self.lookup_data.get('contract_types'))
        _populate(self.management_combo, self.lookup_data.get('managements'))
        _populate(self.activity_combo, self.lookup_data.get('activities'))

    def set_data(self, car):
        self.setWindowTitle("تحديث بيانات السيارة")
        self.fleet_no_input.setText(car.fleet_no)
        self.plate_no_en_input.setText(car.plate_no_en)
        self.plate_no_ar_input.setText(car.plate_no_ar)
        self.address_details_input.setText(car.address_details_1)
        
        def _set_combo(combo, value): combo.setCurrentIndex(combo.findData(value) or 0)
        _set_combo(self.department_combo, car.department_id)
        _set_combo(self.carclass_combo, car.car_class_id)
        _set_combo(self.manufacturer_combo, car.manufacturer_id)
        _set_combo(self.model_combo, car.model_id)
        _set_combo(self.functionallocation_combo, car.functional_location_id)
        _set_combo(self.locationdescription_combo, car.location_description_id)
        _set_combo(self.notificationrecipient_combo, car.notification_recipient_id)
        _set_combo(self.contracttype_combo, car.contract_type_id)
        _set_combo(self.management_combo, car.management_id)
        _set_combo(self.activity_combo, car.activity_id)

        self.owned_radio.setChecked(car.ownership == OwnershipStatus.OWNED)
        self.leased_radio.setChecked(car.ownership == OwnershipStatus.LEASED)
        self.regular_radio.setChecked(car.room_type == RoomType.REGULAR)
        self.non_regular_radio.setChecked(car.room_type == RoomType.NON_REGULAR)
        self.emp_24hrs_radio.setChecked(car.room_type == RoomType.EMP_24HRS)

        def _set_date(date_widget, value): date_widget.setDate(value or QDate.currentDate())
        _set_date(self.registration_start_date, car.registration_start_date)
        _set_date(self.registration_end_date, car.registration_end_date)
        _set_date(self.inspection_start_date, car.inspection_start_date)
        _set_date(self.inspection_end_date, car.inspection_end_date)
        
        self.image_path = "placeholder.jpg" # Dummy value for existing image
        self.image_preview_label.setText("صورة موجودة بالفعل\n(اختر واحدة جديدة لتغييرها)")

    def get_data(self):
        return {
            "fleet_no": self.fleet_no_input.text().strip(),
            "plate_no_en": self.plate_no_en_input.text().strip(),
            "plate_no_ar": self.plate_no_ar_input.text().strip(),
            "address_details_1": self.address_details_input.toPlainText().strip(),
            "ownership": OwnershipStatus.OWNED if self.owned_radio.isChecked() else (OwnershipStatus.LEASED if self.leased_radio.isChecked() else None),
            "room_type": RoomType.REGULAR if self.regular_radio.isChecked() else (RoomType.NON_REGULAR if self.non_regular_radio.isChecked() else (RoomType.EMP_24HRS if self.emp_24hrs_radio.isChecked() else None)),
            "department_id": self.department_combo.currentData(),
            "car_class_id": self.carclass_combo.currentData(),
            "manufacturer_id": self.manufacturer_combo.currentData(),
            "model_id": self.model_combo.currentData(),
            "functional_location_id": self.functionallocation_combo.currentData(),
            "location_description_id": self.locationdescription_combo.currentData(),
            "notification_recipient_id": self.notificationrecipient_combo.currentData(),
            "contract_type_id": self.contracttype_combo.currentData(),
            "management_id": self.management_combo.currentData(),
            "activity_id": self.activity_combo.currentData(),
            "registration_start_date": self.registration_start_date.date().toPyDate(),
            "registration_end_date": self.registration_end_date.date().toPyDate(),
            "inspection_start_date": self.inspection_start_date.date().toPyDate(),
            "inspection_end_date": self.inspection_end_date.date().toPyDate(),
            "image_path": self.image_path
        }

    def accept(self):
        data = self.get_data()
        required_text = {"رقم الأسطول": data["fleet_no"], "رقم اللوحة (EN)": data["plate_no_en"], "رقم اللوحة (AR)": data["plate_no_ar"], "تفاصيل العنوان": data["address_details_1"]}
        for name, value in required_text.items():
            if not value:
                QMessageBox.warning(self, "خطأ في الإدخال", f"حقل '{name}' لا يمكن أن يكون فارغاً."); return
        
        required_combos = {"الإدارة (Code)": data["department_id"], "الفئة": data["car_class_id"], "المصنع": data["manufacturer_id"]}
        for name, value in required_combos.items():
            if value is None:
                QMessageBox.warning(self, "خطأ في الإدخال", f"يجب اختيار قيمة في حقل '{name}'."); return
                
        if not data["image_path"]:
            QMessageBox.warning(self, "خطأ في الإدخال", "يجب تحديد صورة للسيارة."); return

        super().accept()