#!/usr/bin/env python3
"""
BioScript - Resept Yazma Workflow
Barmaq izi oxuma, pasiyent məlumatları və yeni resept yazma
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QFrame, QGridLayout, QListWidget,
                            QTextEdit, QLineEdit, QScrollArea, QSplitter,
                            QGroupBox, QListWidgetItem, QProgressBar,
                            QTabWidget, QTableWidget, QTableWidgetItem,
                            QMessageBox, QDialog, QFormLayout, QComboBox,
                            QSpinBox, QDateEdit, QPlainTextEdit)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QDate
from PyQt5.QtGui import QFont, QColor, QPalette
from datetime import datetime, date
import threading

from fingerprint_reader import FingerprintSimulator
from real_fingerprint import RealFingerprintReader
from gemini_ai import BioScriptAI

class FingerprintScanDialog(QDialog):
    """Barmaq izi oxuma dialoqu"""
    
    fingerprint_scanned = pyqtSignal(dict)  # patient_data
    
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        # Real barmaq izi oxuyucu istifadə etməyə çalış
        try:
            self.fingerprint_reader = RealFingerprintReader()
            if not self.fingerprint_reader.connect():
                print("⚠️ Real oxuyucu bağlanmadı, simulatora keçilir")
                self.fingerprint_reader = FingerprintSimulator()
        except Exception as e:
            print(f"Real oxuyucu xətası: {e}")
            self.fingerprint_reader = FingerprintSimulator()
        self.init_ui()
        
    def init_ui(self):
        """UI yaratma"""
        self.setWindowTitle("Barmaq İzi Oxuma")
        self.setFixedSize(400, 300)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Başlıq
        title = QLabel("🔍 Barmaq İzi Oxuma")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #1e88e5; margin-bottom: 20px;")
        
        # Barmaq izi icon
        fingerprint_icon = QLabel("👆")
        fingerprint_icon.setFont(QFont("Arial", 72))
        fingerprint_icon.setAlignment(Qt.AlignCenter)
        fingerprint_icon.setStyleSheet("margin: 20px;")
        
        # Status
        self.status_label = QLabel("Arduino bağlantısı qurulur...")
        self.status_label.setFont(QFont("Arial", 12))
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #666; margin: 10px;")
        
        # Progress bar
        self.progress = QProgressBar()
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #1e88e5;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #1e88e5;
                width: 20px;
            }
        """)
        
        # Düymələr
        button_layout = QHBoxLayout()
        
        self.scan_btn = QPushButton("🔍 Oxumağa Başla")
        self.scan_btn.setFont(QFont("Segoe UI", 13, QFont.Bold))
        self.scan_btn.setFixedSize(180, 45)
        self.scan_btn.clicked.connect(self.start_scanning)
        self.scan_btn.setEnabled(False)
        self.scan_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #1e88e5, stop:1 #1565c0);
                color: white;
                border: none;
                border-radius: 12px;
                padding: 12px 25px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #42a5f5, stop:1 #1e88e5);
            }
            QPushButton:disabled {
                background: #ccc;
                color: #999;
            }
        """)
        
        cancel_btn = QPushButton("❌ Ləğv et")
        cancel_btn.setFont(QFont("Segoe UI", 13, QFont.Bold))
        cancel_btn.setFixedSize(180, 45)
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #f44336, stop:1 #d32f2f);
                color: white;
                border: none;
                border-radius: 12px;
                padding: 12px 25px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #ef5350, stop:1 #f44336);
            }
        """)
        
        button_layout.addStretch()
        button_layout.addWidget(self.scan_btn)
        button_layout.addWidget(cancel_btn)
        button_layout.addStretch()
        
        # Layout-a əlavə etmə
        layout.addWidget(title)
        layout.addWidget(fingerprint_icon)
        layout.addWidget(self.status_label)
        layout.addWidget(self.progress)
        layout.addLayout(button_layout)
        
        # Arduino bağlantısını başlat
        QTimer.singleShot(1000, self.connect_arduino)
        
    def connect_arduino(self):
        """Arduino bağlantısı"""
        self.status_label.setText("Arduino ilə bağlanılır...")
        self.progress.setValue(25)
        
        if self.fingerprint_reader.connect():
            self.status_label.setText("✅ Arduino hazır. Barmağınızı sensora qoyun və oxuma düyməsinə basın.")
            self.progress.setValue(100)
            self.scan_btn.setEnabled(True)
            self.scan_btn.setText("🔍 Barmaq İzi Oxu")
        else:
            self.status_label.setText("❌ Arduino bağlantısı uğursuz oldu. Simulator istifadə ediləcək.")
            self.progress.setValue(50)
            self.scan_btn.setEnabled(True)
            self.scan_btn.setText("🔍 Simulator Oxu")
            
    def start_scanning(self):
        """Oxuma prosesini başlatma"""
        self.scan_btn.setEnabled(False)
        self.status_label.setText("🔍 Barmaq izi oxunur...")
        self.progress.setValue(50)
        
        # Başqa thread-də oxu
        threading.Thread(target=self.scan_fingerprint, daemon=True).start()
        
    def scan_fingerprint(self):
        """Barmaq izi oxuma"""
        try:
            finger_id, message = self.fingerprint_reader.capture_fingerprint()
            
            if finger_id:
                # Pasiyent tap
                patient = self.fingerprint_reader.find_patient_by_fingerprint(finger_id)
                
                if patient:
                    self.status_label.setText(f"✅ Pasiyent tapıldı: {patient['name']}")
                    self.progress.setValue(100)
                    
                    # 2 saniyə gözlə və yayın
                    QTimer.singleShot(2000, lambda: self.fingerprint_scanned.emit(patient))
                    QTimer.singleShot(2500, self.accept)
                else:
                    self.status_label.setText("❌ Bu barmaq izi qeydiyyatlı deyil")
                    self.progress.setValue(0)
                    self.scan_btn.setEnabled(True)
                    self.scan_btn.setText("Yenidən Cəhd Et")
            else:
                self.status_label.setText(f"❌ {message}")
                self.progress.setValue(0)
                self.scan_btn.setEnabled(True)
                self.scan_btn.setText("Yenidən Cəhd Et")
                
        except Exception as e:
            self.status_label.setText(f"❌ Xəta: {str(e)}")
            self.progress.setValue(0)
            self.scan_btn.setEnabled(True)

class PatientHistoryWidget(QWidget):
    """Pasiyent tarixçəsi"""
    
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.current_patient = None
        self.init_ui()
        
    def init_ui(self):
        """UI yaratma"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # Pasiyent məlumatları
        self.patient_info_frame = QGroupBox("Pasiyent Məlumatları")
        self.patient_info_frame.setFont(QFont("Arial", 12, QFont.Bold))
        patient_info_layout = QFormLayout(self.patient_info_frame)
        
        self.name_label = QLabel("-")
        self.fin_label = QLabel("-")
        self.birth_label = QLabel("-")
        self.phone_label = QLabel("-")
        
        patient_info_layout.addRow("Ad Soyad:", self.name_label)
        patient_info_layout.addRow("FİN:", self.fin_label)
        patient_info_layout.addRow("Doğum tarixi:", self.birth_label)
        patient_info_layout.addRow("Telefon:", self.phone_label)
        
        # Resept tarixçəsi
        history_frame = QGroupBox("Resept Tarixçəsi")
        history_frame.setFont(QFont("Arial", 12, QFont.Bold))
        history_layout = QVBoxLayout(history_frame)
        
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(4)
        self.history_table.setHorizontalHeaderLabels(["Tarix", "Diaqnoz", "Həkim", "Dərman Sayı"])
        self.history_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.history_table.itemClicked.connect(self.show_prescription_details)
        
        history_layout.addWidget(self.history_table)
        
        # Layout-a əlavə etmə
        layout.addWidget(self.patient_info_frame)
        layout.addWidget(history_frame)
        
    def set_patient(self, patient_data):
        """Pasiyenti təyin etmə"""
        self.current_patient = patient_data
        
        # Məlumatları doldur
        self.name_label.setText(patient_data.get('name', '-'))
        self.fin_label.setText(patient_data.get('fin_code', '-'))
        self.birth_label.setText(str(patient_data.get('birth_date', '-')))
        self.phone_label.setText(patient_data.get('phone', '-'))
        
        # Resept tarixçəsini yüklə
        self.load_prescription_history()
        
    def load_prescription_history(self):
        """Resept tarixçəsini yükləmə"""
        if not self.current_patient:
            return
            
        try:
            prescriptions = self.db_manager.get_patient_prescriptions(
                self.current_patient['id']
            )
            
            self.history_table.setRowCount(len(prescriptions))
            
            for row, prescription in enumerate(prescriptions):
                # Tarix
                date_item = QTableWidgetItem(str(prescription.get('issued_at', '')))
                self.history_table.setItem(row, 0, date_item)
                
                # Diaqnoz
                diagnosis_item = QTableWidgetItem(prescription.get('diagnosis', '-'))
                self.history_table.setItem(row, 1, diagnosis_item)
                
                # Həkim
                doctor_name = f"Dr. {prescription.get('doctor_name', '')} {prescription.get('doctor_surname', '')}"
                doctor_item = QTableWidgetItem(doctor_name)
                self.history_table.setItem(row, 2, doctor_item)
                
                # Dərman sayı
                med_count = len(prescription.get('medications', []))
                med_item = QTableWidgetItem(str(med_count))
                self.history_table.setItem(row, 3, med_item)
                
        except Exception as e:
            print(f"Resept tarixçəsi yükləmə xətası: {e}")
            
    def show_prescription_details(self, item):
        """Resept detallarını göstərmə"""
        row = item.row()
        # Bu funksionallığı gələcəkdə genişləndirə bilərik
        pass

class NewPrescriptionWidget(QWidget):
    """Yeni resept yazma"""
    
    prescription_saved = pyqtSignal(dict)
    
    def __init__(self, db_manager, ai_assistant):
        super().__init__()
        self.db_manager = db_manager
        self.ai_assistant = ai_assistant
        self.current_patient = None
        self.current_doctor = None
        self.medications = []
        self.init_ui()
        
    def init_ui(self):
        """UI yaratma"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(20)
        
        # Resept məlumatları
        prescription_frame = QGroupBox("Resept Məlumatları")
        prescription_frame.setFont(QFont("Arial", 12, QFont.Bold))
        prescription_layout = QFormLayout(prescription_frame)
        
        # Şikayət
        self.complaint_input = QPlainTextEdit()
        self.complaint_input.setMaximumHeight(80)
        self.complaint_input.setPlaceholderText("Xəstənin şikayətlərini daxil edin...")
        
        # Diaqnoz
        self.diagnosis_input = QPlainTextEdit()
        self.diagnosis_input.setMaximumHeight(80)
        self.diagnosis_input.setPlaceholderText("Qoyulan diaqnozu daxil edin...")
        
        prescription_layout.addRow("Şikayət:", self.complaint_input)
        prescription_layout.addRow("Diaqnoz:", self.diagnosis_input)
        
        # Dərmanlar
        medications_frame = QGroupBox("Dərmanlar")
        medications_frame.setFont(QFont("Arial", 12, QFont.Bold))
        medications_layout = QVBoxLayout(medications_frame)
        
        # Dərman əlavə etmə
        add_med_layout = QHBoxLayout()
        
        add_med_btn = QPushButton("+ Dərman Əlavə Et")
        add_med_btn.clicked.connect(self.add_medication)
        add_med_btn.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        
        add_med_layout.addWidget(add_med_btn)
        add_med_layout.addStretch()
        
        # Dərman siyahısı
        self.medications_list = QListWidget()
        self.medications_list.setMaximumHeight(150)
        
        medications_layout.addLayout(add_med_layout)
        medications_layout.addWidget(self.medications_list)
        
        # Qeyd etmə düyməsi
        save_layout = QHBoxLayout()
        save_layout.addStretch()
        
        save_btn = QPushButton("Resepti Qeyd Et")
        save_btn.setFixedSize(150, 40)
        save_btn.setFont(QFont("Arial", 12, QFont.Bold))
        save_btn.clicked.connect(self.save_prescription)
        save_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #1e88e5, stop:1 #1976d2);
                color: white;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #1976d2, stop:1 #1565c0);
            }
        """)
        
        save_layout.addWidget(save_btn)
        
        # Layout-a əlavə etmə
        layout.addWidget(prescription_frame)
        layout.addWidget(medications_frame)
        layout.addLayout(save_layout)
        layout.addStretch()
        
    def set_patient_and_doctor(self, patient_data, doctor_data):
        """Pasiyent və həkimi təyin etmə"""
        self.current_patient = patient_data
        self.current_doctor = doctor_data
        
        # Formu sıfırla
        self.complaint_input.clear()
        self.diagnosis_input.clear()
        self.medications.clear()
        self.medications_list.clear()
        
    def add_medication(self):
        """Dərman əlavə etmə dialoqu"""
        dialog = MedicationDialog()
        if dialog.exec_() == QDialog.Accepted:
            medication_data = dialog.get_medication_data()
            self.medications.append(medication_data)
            
            # Siyahıya əlavə et
            med_text = f"{medication_data['name']} - {medication_data['dosage']} - {medication_data['frequency']}"
            self.medications_list.addItem(med_text)
    
    def save_prescription(self):
        """Resepti saxlama"""
        if not self.current_patient or not self.current_doctor:
            QMessageBox.warning(self, "Xəta", "Pasiyent və ya həkim seçilməyib!")
            return
            
        complaint = self.complaint_input.toPlainText().strip()
        diagnosis = self.diagnosis_input.toPlainText().strip()
        
        if not complaint or not diagnosis:
            QMessageBox.warning(self, "Xəta", "Şikayət və diaqnoz daxil edilməlidir!")
            return
            
        if not self.medications:
            QMessageBox.warning(self, "Xəta", "Ən azı bir dərman əlavə edilməlidir!")
            return
        
        # Resept məlumatları
        prescription_data = {
            'doctor_id': self.current_doctor['id'],
            'patient_id': self.current_patient['id'],
            'complaint': complaint,
            'diagnosis': diagnosis,
            'medications': self.medications
        }
        
        # Saxla
        prescription_id = self.db_manager.create_prescription(prescription_data)
        
        if prescription_id:
            QMessageBox.information(self, "Uğur", "Resept uğurla qeyd edildi!")
            self.prescription_saved.emit(prescription_data)
            
            # Formu təmizlə
            self.complaint_input.clear()
            self.diagnosis_input.clear()
            self.medications.clear()
            self.medications_list.clear()
        else:
            QMessageBox.critical(self, "Xəta", "Resept qeyd edilə bilmədi!")

class MedicationDialog(QDialog):
    """Dərman əlavə etmə dialoqu"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        """UI yaratma"""
        self.setWindowTitle("Dərman Əlavə Et")
        self.setFixedSize(400, 300)
        
        layout = QFormLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Dərman adı
        self.name_combo = QComboBox()
        self.name_combo.setEditable(True)
        
        # Yaygın dərmanlar
        common_medications = [
            "Paracetamol", "Aspirin", "Ibuprofen", "Amoxicillin",
            "Metformin", "Atorvastatin", "Omeprazole", "Amlodipine"
        ]
        self.name_combo.addItems(common_medications)
        
        # Dozaj
        self.dosage_input = QLineEdit()
        self.dosage_input.setPlaceholderText("məs: 500mg")
        
        # Tezlik
        self.frequency_combo = QComboBox()
        self.frequency_combo.addItems([
            "Gündə 1 dəfə",
            "Gündə 2 dəfə", 
            "Gündə 3 dəfə",
            "Gündə 4 dəfə",
            "Hər 6 saatda bir",
            "Hər 8 saatda bir",
            "Lazım olduqda"
        ])
        
        # Müddət
        self.duration_combo = QComboBox()
        self.duration_combo.addItems([
            "3 gün", "5 gün", "7 gün", "10 gün",
            "14 gün", "21 gün", "1 ay", "3 ay"
        ])
        
        # İstifadə qaydası
        self.instructions_input = QLineEdit()
        self.instructions_input.setPlaceholderText("Yeməkdən sonra, su ilə")
        
        # Düymələr
        button_layout = QHBoxLayout()
        
        ok_btn = QPushButton("Təsdiq")
        ok_btn.clicked.connect(self.accept)
        
        cancel_btn = QPushButton("Ləğv")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        
        # Layout-a əlavə etmə
        layout.addRow("Dərman adı:", self.name_combo)
        layout.addRow("Dozaj:", self.dosage_input)
        layout.addRow("Tezlik:", self.frequency_combo)
        layout.addRow("Müddət:", self.duration_combo)
        layout.addRow("İstifadə qaydası:", self.instructions_input)
        layout.addRow("", button_layout)
        
    def get_medication_data(self):
        """Dərman məlumatlarını alma"""
        return {
            'medication_name': self.name_combo.currentText(),
            'dosage': self.dosage_input.text(),
            'frequency': self.frequency_combo.currentText(),
            'duration': self.duration_combo.currentText(),
            'instructions': self.instructions_input.text()
        }