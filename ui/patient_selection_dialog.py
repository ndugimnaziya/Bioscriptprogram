#!/usr/bin/env python3
"""
BioScript - Pasiyent Seçim Dialoqu
Pasiyent listi və yeni pasiyent yaratma
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QFrame, QListWidget, QListWidgetItem,
                            QLineEdit, QTextEdit, QFormLayout, QDateEdit,
                            QComboBox, QMessageBox, QGroupBox, QScrollArea)
from PyQt5.QtCore import Qt, pyqtSignal, QDate
from PyQt5.QtGui import QFont
from datetime import datetime, date
import random

class PatientSelectionDialog(QDialog):
    """Pasiyent seçim dialoqu"""
    
    patient_selected = pyqtSignal(dict)  # seçilən pasiyent məlumatları
    
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.selected_patient = None
        self.init_ui()
        self.load_patients()
        
    def init_ui(self):
        """UI yaratma"""
        self.setWindowTitle("👥 Pasiyent Seçimi - BioScript")
        self.setFixedSize(800, 600)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Başlıq
        title = QLabel("👥 Pasiyent Seçimi")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            color: #1565c0; 
            margin-bottom: 20px;
            padding: 15px;
            background: #e3f2fd;
            border-radius: 15px;
        """)
        layout.addWidget(title)
        
        # Axtarış sahəsi
        search_layout = QHBoxLayout()
        search_label = QLabel("🔍 Axtarış:")
        search_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Ad, soyad və ya ID nömrəsi daxil edin...")
        self.search_input.textChanged.connect(self.filter_patients)
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #1e88e5;
                border-radius: 8px;
                font-size: 14px;
            }
        """)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        # Pasiyent listi
        self.patient_list = QListWidget()
        self.patient_list.setStyleSheet("""
            QListWidget {
                border: 2px solid #e0e0e0;
                border-radius: 10px;
                background: #fafafa;
                padding: 10px;
                font-family: 'Segoe UI';
                font-size: 14px;
            }
            QListWidget::item {
                padding: 15px;
                border-bottom: 1px solid #e0e0e0;
                border-radius: 8px;
                margin: 3px 0;
                background: white;
            }
            QListWidget::item:hover {
                background: #f0f8ff;
                border: 2px solid #64b5f6;
            }
            QListWidget::item:selected {
                background: #e3f2fd;
                color: #1565c0;
                border: 2px solid #1e88e5;
                font-weight: bold;
            }
        """)
        self.patient_list.itemClicked.connect(self.on_patient_selected)
        layout.addWidget(self.patient_list)
        
        # Düymələr
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        # Yeni pasiyent düyməsi
        self.new_patient_btn = QPushButton("➕ Yeni Pasiyent")
        self.new_patient_btn.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.new_patient_btn.setFixedHeight(50)
        self.new_patient_btn.clicked.connect(self.create_new_patient)
        self.new_patient_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #4caf50, stop:1 #388e3c);
                color: white;
                border: none;
                border-radius: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #66bb6a, stop:1 #4caf50);
            }
        """)
        
        # Seç düyməsi
        self.select_btn = QPushButton("✅ Seç")
        self.select_btn.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.select_btn.setFixedHeight(50)
        self.select_btn.clicked.connect(self.confirm_selection)
        self.select_btn.setEnabled(False)
        self.select_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #1e88e5, stop:1 #1976d2);
                color: white;
                border: none;
                border-radius: 10px;
                font-weight: bold;
            }
            QPushButton:hover:enabled {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #42a5f5, stop:1 #1e88e5);
            }
            QPushButton:disabled {
                background: #cccccc;
                color: #666666;
            }
        """)
        
        # Ləğv et düyməsi
        self.cancel_btn = QPushButton("❌ Ləğv Et")
        self.cancel_btn.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.cancel_btn.setFixedHeight(50)
        self.cancel_btn.clicked.connect(self.reject)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #f44336, stop:1 #d32f2f);
                color: white;
                border: none;
                border-radius: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #ef5350, stop:1 #f44336);
            }
        """)
        
        button_layout.addWidget(self.new_patient_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.select_btn)
        
        layout.addLayout(button_layout)
        
    def load_patients(self):
        """Pasiyentləri yüklə"""
        try:
            # Pasiyent məlumatlarını verilənlər bazasından al
            connection = self.db_manager.get_connection()
            if not connection or not connection.is_connected():
                QMessageBox.warning(self, "Verilənlər Bazası Xətası", 
                                  "Verilənlər bazasına bağlantı yoxdur!")
                return
            cursor = connection.cursor(dictionary=True)
            
            query = """
            SELECT id, name as ad, fin_code as soyad, birth_date as doğum_tarixi, 
                   phone as telefon, '' as email, address as ünvan
            FROM patients 
            ORDER BY name, fin_code
            """
            cursor.execute(query)
            patients = cursor.fetchall()
            
            self.patient_list.clear()
            
            for patient in patients:
                patient_id, ad, soyad, dogum_tarixi, telefon, email, unvan = patient
                
                # Yaş hesabla
                if dogum_tarixi:
                    today = date.today()
                    yas = today.year - dogum_tarixi.year - ((today.month, today.day) < (dogum_tarixi.month, dogum_tarixi.day))
                else:
                    yas = "Bilinmir"
                
                # List item mətnini format et
                item_text = f"""
                📋 {ad} {soyad} (ID: {patient_id})
                🎂 Yaş: {yas}   📞 Tel: {telefon or 'Yoxdur'}
                📧 Email: {email or 'Yoxdur'}
                🏠 Ünvan: {unvan or 'Yoxdur'}
                """
                
                item = QListWidgetItem(item_text.strip())
                # Pasiyent məlumatlarını item data kimi saxla
                item.setData(Qt.UserRole, {
                    'id': patient_id,
                    'ad': ad,
                    'soyad': soyad,
                    'doğum_tarixi': dogum_tarixi,
                    'telefon': telefon,
                    'email': email,
                    'ünvan': unvan,
                    'yaş': yas
                })
                
                self.patient_list.addItem(item)
                
            cursor.close()
            connection.close()
            
        except Exception as e:
            QMessageBox.warning(self, "Xəta", f"Pasiyentlər yüklənərkən xəta: {str(e)}")
            
    def filter_patients(self):
        """Pasiyentləri axtarış sözünə görə filtrləmə"""
        search_text = self.search_input.text().lower()
        
        for i in range(self.patient_list.count()):
            item = self.patient_list.item(i)
            item_text = item.text().lower()
            
            # Ad, soyad və ya ID-də axtarış söz var?
            if search_text in item_text:
                item.setHidden(False)
            else:
                item.setHidden(True)
                
    def on_patient_selected(self, item):
        """Pasiyent seçiləndə"""
        self.selected_patient = item.data(Qt.UserRole)
        self.select_btn.setEnabled(True)
        
    def confirm_selection(self):
        """Seçimi təsdiq et"""
        if self.selected_patient:
            self.patient_selected.emit(self.selected_patient)
            self.accept()
            
    def create_new_patient(self):
        """Yeni pasiyent yaratma dialoqu"""
        dialog = NewPatientDialog(self.db_manager)
        if dialog.exec_() == QDialog.Accepted:
            # Yeni pasiyent yaradıldı, listi yenilə
            self.load_patients()


class NewPatientDialog(QDialog):
    """Yeni pasiyent yaratma dialoqu"""
    
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.init_ui()
        
    def init_ui(self):
        """UI yaratma"""
        self.setWindowTitle("➕ Yeni Pasiyent - BioScript")
        self.setFixedSize(500, 600)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Başlıq
        title = QLabel("➕ Yeni Pasiyent Qeydiyyatı")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            color: #1565c0; 
            margin-bottom: 15px;
            padding: 12px;
            background: #e3f2fd;
            border-radius: 12px;
        """)
        layout.addWidget(title)
        
        # Form
        form_frame = QGroupBox("Pasiyent Məlumatları")
        form_frame.setFont(QFont("Segoe UI", 12, QFont.Bold))
        form_frame.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e3f2fd;
                border-radius: 10px;
                margin: 10px;
                padding: 15px;
                background: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px;
                color: #1565c0;
                background: white;
            }
        """)
        
        form_layout = QFormLayout(form_frame)
        form_layout.setSpacing(15)
        
        # Form sahələri
        self.ad_input = QLineEdit()
        self.ad_input.setPlaceholderText("Məsələn: Əhməd")
        
        self.soyad_input = QLineEdit()
        self.soyad_input.setPlaceholderText("Məsələn: 1234567")  # FIN kod
        
        self.dogum_date = QDateEdit()
        self.dogum_date.setDate(QDate.currentDate().addYears(-30))
        self.dogum_date.setDisplayFormat("dd.MM.yyyy")
        self.dogum_date.setCalendarPopup(True)
        
        self.cinsi_combo = QComboBox()
        self.cinsi_combo.addItems(["Kişi", "Qadın", "Digər"])
        
        self.telefon_input = QLineEdit()
        self.telefon_input.setPlaceholderText("Məsələn: +994 50 123 45 67")
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Məsələn: ahmed@example.com")
        
        self.unvan_input = QTextEdit()
        self.unvan_input.setPlaceholderText("Tam ünvan daxil edin...")
        self.unvan_input.setMaximumHeight(80)
        
        # Input stilləri
        input_style = """
            QLineEdit, QDateEdit, QComboBox, QTextEdit {
                padding: 8px;
                border: 2px solid #e0e0e0;
                border-radius: 6px;
                font-size: 14px;
                background: white;
            }
            QLineEdit:focus, QDateEdit:focus, QComboBox:focus, QTextEdit:focus {
                border-color: #1e88e5;
            }
        """
        
        for widget in [self.ad_input, self.soyad_input, self.dogum_date, 
                      self.cinsi_combo, self.telefon_input, self.email_input, 
                      self.unvan_input]:
            widget.setStyleSheet(input_style)
        
        # Form əlavə et
        form_layout.addRow("📝 Ad *:", self.ad_input)
        form_layout.addRow("📝 FIN Kod *:", self.soyad_input)  # FIN kod sahəsi
        form_layout.addRow("🎂 Doğum Tarixi:", self.dogum_date)
        form_layout.addRow("📞 Telefon:", self.telefon_input)
        form_layout.addRow("🏠 Ünvan:", self.unvan_input)
        
        layout.addWidget(form_frame)
        
        # Düymələr
        button_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("💾 Yadda Saxla")
        self.save_btn.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.save_btn.setFixedHeight(45)
        self.save_btn.clicked.connect(self.save_patient)
        self.save_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #4caf50, stop:1 #388e3c);
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #66bb6a, stop:1 #4caf50);
            }
        """)
        
        self.cancel_btn = QPushButton("❌ Ləğv Et")
        self.cancel_btn.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.cancel_btn.setFixedHeight(45)
        self.cancel_btn.clicked.connect(self.reject)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #f44336, stop:1 #d32f2f);
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #ef5350, stop:1 #f44336);
            }
        """)
        
        button_layout.addWidget(self.cancel_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.save_btn)
        
        layout.addLayout(button_layout)
        
    def save_patient(self):
        """Pasiyenti yadda saxla"""
        # Məcburi sahələri yoxla
        if not self.ad_input.text().strip():
            QMessageBox.warning(self, "Xəta", "Ad sahəsi boş ola bilməz!")
            return
            
        if not self.soyad_input.text().strip():
            QMessageBox.warning(self, "Xəta", "FIN kod sahəsi boş ola bilməz!")
            return
            
        try:
            connection = self.db_manager.get_connection()
            if not connection or not connection.is_connected():
                QMessageBox.critical(self, "Verilənlər Bazası Xətası", 
                                   "Verilənlər bazasına bağlantı yoxdur!")
                return
            cursor = connection.cursor(dictionary=True)
            
            # Pasiyenti əlavə et
            query = """
            INSERT INTO patients (id, name, fin_code, birth_date, phone, address)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            
            # Yeni pasiyent ID yaradırıq
            patient_id = f"PAT{random.randint(100, 999):03d}"
            
            values = (
                patient_id,
                self.ad_input.text().strip(),
                self.soyad_input.text().strip(),  # fin_code kimi saxlanacaq
                self.dogum_date.date().toPyDate(),
                self.telefon_input.text().strip() or None,
                self.unvan_input.toPlainText().strip() or None
            )
            
            cursor.execute(query, values)
            connection.commit()
            
            cursor.close()
            connection.close()
            
            QMessageBox.information(self, "Uğur", "Pasiyent uğurla qeydiyyatdan keçdi!")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Xəta", f"Pasiyent qeydiyyatında xəta: {str(e)}")