"""
BioScript - Pasiyent Axtarış Pəncərəsi
Pasiyent axtarışı və seçimi interfeysi
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
                            QFrame, QGroupBox, QFormLayout, QTextEdit,
                            QDateEdit, QComboBox, QMessageBox, QSplitter,
                            QHeaderView, QAbstractItemView)
from PyQt5.QtCore import Qt, pyqtSignal, QDate, QTimer
from PyQt5.QtGui import QFont

class PatientSearchWidget(QWidget):
    """Pasiyent axtarış widget"""
    
    patient_selected = pyqtSignal(dict)
    
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.current_patients = []
        
        # Axtarış gecikməsi üçün timer
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.perform_search)
        
        self.init_ui()
        self.load_initial_data()
    
    def init_ui(self):
        """İstifadəçi interfeysi başlatma"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        
        # Axtarış hissəsi
        self.create_search_section(main_layout)
        
        # Splitter - axtarış nəticələri və detallar
        splitter = QSplitter(Qt.Horizontal)
        
        # Sol tərəf - axtarış nəticələri
        self.create_results_section(splitter)
        
        # Sağ tərəf - pasiyent detalları
        self.create_patient_details_section(splitter)
        
        # Splitter nisbətləri
        splitter.setStretchFactor(0, 2)  # Nəticələr
        splitter.setStretchFactor(1, 1)  # Detallar
        
        main_layout.addWidget(splitter)
        
        # Düymələr
        self.create_action_buttons(main_layout)
    
    def create_search_section(self, parent_layout):
        """Axtarış hissəsi yaratma"""
        search_group = QGroupBox("Pasiyent Axtarışı")
        search_layout = QHBoxLayout(search_group)
        
        # Axtarış sahəsi
        search_label = QLabel("Axtarış:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Ad, soyad, telefon və ya şəxsiyyət nömrəsi daxil edin...")
        self.search_input.textChanged.connect(self.on_search_text_changed)
        
        # Axtarış düyməsi
        search_button = QPushButton("🔍 Axtar")
        search_button.clicked.connect(self.perform_search)
        
        # Təmizlə düyməsi
        clear_button = QPushButton("Təmizlə")
        clear_button.clicked.connect(self.clear_search)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input, 1)
        search_layout.addWidget(search_button)
        search_layout.addWidget(clear_button)
        
        parent_layout.addWidget(search_group)
    
    def create_results_section(self, parent_widget):
        """Axtarış nəticələri hissəsi"""
        results_frame = QFrame()
        results_layout = QVBoxLayout(results_frame)
        
        # Başlıq
        results_label = QLabel("Axtarış Nəticələri")
        results_label.setFont(QFont("Arial", 12, QFont.Bold))
        results_layout.addWidget(results_label)
        
        # Nəticələr cədvəli
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(6)
        self.results_table.setHorizontalHeaderLabels([
            "ID", "Ad", "Soyad", "Doğum tarixi", "Telefon", "Şəxsiyyət"
        ])
        
        # Cədvəl parametrləri
        self.results_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.results_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.results_table.setAlternatingRowColors(True)
        self.results_table.setSortingEnabled(True)
        
        # Sütun genişlikləri
        header = self.results_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Ad
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # Soyad
        
        # Seçim hadisəsi
        self.results_table.itemSelectionChanged.connect(self.on_patient_selection_changed)
        self.results_table.itemDoubleClicked.connect(self.select_patient)
        
        results_layout.addWidget(self.results_table)
        
        # Nəticə sayı
        self.result_count_label = QLabel("0 pasiyent tapıldı")
        self.result_count_label.setStyleSheet("color: #6c757d; font-style: italic;")
        results_layout.addWidget(self.result_count_label)
        
        parent_widget.addWidget(results_frame)
    
    def create_patient_details_section(self, parent_widget):
        """Pasiyent detalları hissəsi"""
        details_frame = QFrame()
        details_layout = QVBoxLayout(details_frame)
        
        # Başlıq
        details_label = QLabel("Pasiyent Detalları")
        details_label.setFont(QFont("Arial", 12, QFont.Bold))
        details_layout.addWidget(details_label)
        
        # Detallar scroll area
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setMaximumHeight(300)
        details_layout.addWidget(self.details_text)
        
        # Pasiyent məlumatları formu (seçildikdə)
        self.patient_form_group = QGroupBox("Pasiyent Məlumatları")
        self.patient_form_group.setVisible(False)
        
        form_layout = QFormLayout(self.patient_form_group)
        
        # Form sahələri
        self.patient_name_label = QLabel()
        self.patient_birth_label = QLabel()
        self.patient_gender_label = QLabel()
        self.patient_phone_label = QLabel()
        self.patient_address_label = QLabel()
        self.patient_blood_type_label = QLabel()
        
        form_layout.addRow("Ad və Soyad:", self.patient_name_label)
        form_layout.addRow("Doğum tarixi:", self.patient_birth_label)
        form_layout.addRow("Cinsi:", self.patient_gender_label)
        form_layout.addRow("Telefon:", self.patient_phone_label)
        form_layout.addRow("Ünvan:", self.patient_address_label)
        form_layout.addRow("Qan qrupu:", self.patient_blood_type_label)
        
        details_layout.addWidget(self.patient_form_group)
        details_layout.addStretch()
        
        parent_widget.addWidget(details_frame)
    
    def create_action_buttons(self, parent_layout):
        """Əməliyyat düymələri"""
        button_layout = QHBoxLayout()
        
        # Yeni pasiyent
        new_patient_btn = QPushButton("➕ Yeni Pasiyent")
        new_patient_btn.clicked.connect(self.add_new_patient)
        
        # Seçilmiş pasienti redaktə et
        self.edit_patient_btn = QPushButton("✏️ Redaktə et")
        self.edit_patient_btn.clicked.connect(self.edit_patient)
        self.edit_patient_btn.setEnabled(False)
        
        # Pasienti seç
        self.select_patient_btn = QPushButton("✅ Pasienti Seç")
        self.select_patient_btn.clicked.connect(self.select_patient)
        self.select_patient_btn.setEnabled(False)
        self.select_patient_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
        """)
        
        button_layout.addWidget(new_patient_btn)
        button_layout.addWidget(self.edit_patient_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.select_patient_btn)
        
        parent_layout.addLayout(button_layout)
    
    def on_search_text_changed(self):
        """Axtarış mətni dəyişəndə"""
        # 500ms gecikməylə axtarış et
        self.search_timer.start(500)
    
    def perform_search(self):
        """Axtarış əməliyyatı"""
        search_term = self.search_input.text().strip()
        
        if not search_term:
            self.load_initial_data()
            return
        
        try:
            # Verilənlər bazasından axtarış
            patients = self.db_manager.search_patients(search_term)
            self.display_patients(patients)
            
        except Exception as e:
            QMessageBox.critical(self, "Xəta", f"Axtarış xətası: {str(e)}")
    
    def load_initial_data(self):
        """İlkin məlumatları yükləmə"""
        try:
            # Bütün pasiyentləri gətir (məhdudlaşdırılmış)
            patients = self.db_manager.search_patients("")
            self.display_patients(patients[:50])  # İlk 50 pasiyent
            
        except Exception as e:
            QMessageBox.critical(self, "Xəta", f"Məlumat yükləmə xətası: {str(e)}")
    
    def display_patients(self, patients):
        """Pasiyentləri cədvəldə göstərmə"""
        self.current_patients = patients
        
        # Cədvəli təmizlə
        self.results_table.setRowCount(len(patients))
        
        # Məlumatları doldur
        for row, patient in enumerate(patients):
            self.results_table.setItem(row, 0, QTableWidgetItem(str(patient.get('id', ''))))
            self.results_table.setItem(row, 1, QTableWidgetItem(patient.get('name', '')))
            self.results_table.setItem(row, 2, QTableWidgetItem(patient.get('surname', '')))
            
            birth_date = patient.get('birth_date', '')
            if birth_date:
                birth_date = str(birth_date)
            self.results_table.setItem(row, 3, QTableWidgetItem(birth_date))
            
            self.results_table.setItem(row, 4, QTableWidgetItem(patient.get('phone', '')))
            self.results_table.setItem(row, 5, QTableWidgetItem(patient.get('id_number', '')))
        
        # Nəticə sayını yenilə
        count = len(patients)
        if count == 0:
            self.result_count_label.setText("Heç bir pasiyent tapılmadı")
        elif count == 1:
            self.result_count_label.setText("1 pasiyent tapıldı")
        else:
            self.result_count_label.setText(f"{count} pasiyent tapıldı")
        
        # Cədvəlin genişliyini yenilə
        self.results_table.resizeColumnsToContents()
    
    def on_patient_selection_changed(self):
        """Pasiyent seçimi dəyişəndə"""
        selected_rows = self.results_table.selectionModel().selectedRows()
        
        if selected_rows:
            row = selected_rows[0].row()
            patient = self.current_patients[row]
            
            # Pasiyent detallarını göstər
            self.show_patient_details(patient)
            
            # Düymələri aktiv et
            self.edit_patient_btn.setEnabled(True)
            self.select_patient_btn.setEnabled(True)
        else:
            # Heç nə seçilməyib
            self.clear_patient_details()
            self.edit_patient_btn.setEnabled(False)
            self.select_patient_btn.setEnabled(False)
    
    def show_patient_details(self, patient):
        """Pasiyent detallarını göstərmə"""
        # Mətn formatında detallar
        details_text = f"""
<h3>{patient.get('name', '')} {patient.get('surname', '')}</h3>

<b>Əsas Məlumatlar:</b><br>
• ID: {patient.get('id', '')}<br>
• Doğum tarixi: {patient.get('birth_date', 'Məlum deyil')}<br>
• Cinsi: {patient.get('gender', 'Məlum deyil')}<br>
• Qan qrupu: {patient.get('blood_type', 'Məlum deyil')}<br>

<b>Əlaqə Məlumatları:</b><br>
• Telefon: {patient.get('phone', 'Məlum deyil')}<br>
• Ünvan: {patient.get('address', 'Məlum deyil')}<br>

<b>Tibbi Məlumatlar:</b><br>
• Allergiyalar: {patient.get('allergies', 'Yoxdur')}<br>
• Xroniki xəstəliklər: {patient.get('chronic_diseases', 'Yoxdur')}<br>
• Təcili əlaqə: {patient.get('emergency_contact', 'Məlum deyil')}<br>
        """
        
        self.details_text.setHtml(details_text)
        
        # Form məlumatları
        self.patient_name_label.setText(f"{patient.get('name', '')} {patient.get('surname', '')}")
        self.patient_birth_label.setText(str(patient.get('birth_date', 'Məlum deyil')))
        self.patient_gender_label.setText(patient.get('gender', 'Məlum deyil'))
        self.patient_phone_label.setText(patient.get('phone', 'Məlum deyil'))
        self.patient_address_label.setText(patient.get('address', 'Məlum deyil'))
        self.patient_blood_type_label.setText(patient.get('blood_type', 'Məlum deyil'))
        
        self.patient_form_group.setVisible(True)
    
    def clear_patient_details(self):
        """Pasiyent detallarını təmizləmə"""
        self.details_text.clear()
        self.patient_form_group.setVisible(False)
    
    def clear_search(self):
        """Axtarışı təmizləmə"""
        self.search_input.clear()
        self.load_initial_data()
        self.clear_patient_details()
    
    def select_patient(self):
        """Pasienti seçmə"""
        selected_rows = self.results_table.selectionModel().selectedRows()
        
        if not selected_rows:
            QMessageBox.warning(self, "Xəta", "Pasiyent seçin!")
            return
        
        row = selected_rows[0].row()
        patient = self.current_patients[row]
        
        # Siqnal göndər
        self.patient_selected.emit(patient)
    
    def add_new_patient(self):
        """Yeni pasiyent əlavə etmə"""
        QMessageBox.information(self, "Məlumat", 
                               "Yeni pasiyent əlavə etmə funksiyası hazırlanır...")
    
    def edit_patient(self):
        """Pasienti redaktə etmə"""
        QMessageBox.information(self, "Məlumat", 
                               "Pasiyent redaktə etmə funksiyası hazırlanır...")