#!/usr/bin/env python3
"""
BioScript - Yeni Resept Workflow
Barmaq izi oxuma → Pasiyent məlumatları → Yeni resept yazma
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QFrame, QGridLayout, QListWidget,
                            QTextEdit, QLineEdit, QScrollArea, QSplitter,
                            QGroupBox, QListWidgetItem, QProgressBar,
                            QTabWidget, QTableWidget, QTableWidgetItem,
                            QMessageBox, QDialog, QFormLayout, QComboBox,
                            QSpinBox, QDateEdit, QPlainTextEdit, QStackedWidget)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QDate
from PyQt5.QtGui import QFont, QColor, QPalette
from datetime import datetime, date
import threading

from fingerprint_reader import FingerprintSimulator
from real_fingerprint import RealFingerprintReader
from gemini_ai import BioScriptAI

class FingerprintFirstDialog(QDialog):
    """Barmaq izi oxuma dialoqu - yeni workflow üçün"""
    
    fingerprint_success = pyqtSignal(dict)  # patient_data
    
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
        self.setWindowTitle("🔍 Barmaq İzi İlə Giriş - BioScript")
        self.setFixedSize(500, 400)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(25)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Başlıq
        title = QLabel("🔍 Barmaq İzi Oxuma")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            color: #1565c0; 
            margin-bottom: 20px;
            padding: 15px;
            background: #e3f2fd;
            border-radius: 15px;
        """)
        
        # Barmaq izi icon - daha böyük
        fingerprint_icon = QLabel("👆")
        fingerprint_icon.setFont(QFont("Arial", 100))
        fingerprint_icon.setAlignment(Qt.AlignCenter)
        fingerprint_icon.setStyleSheet("""
            margin: 30px;
            padding: 20px;
            background: #f5f5f5;
            border-radius: 20px;
            border: 3px dashed #1565c0;
        """)
        
        # Status mesajı - daha geniş və aydın
        self.status_label = QLabel("Arduino bağlantısı qurulur...\nXahiş edirik gözləyin")
        self.status_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet("""
            color: #1565c0; 
            margin: 20px;
            padding: 15px;
            background: #e8f5e8;
            border-radius: 12px;
            border: 2px solid #4caf50;
            min-height: 60px;
        """)
        
        # Progress bar - daha böyük və rəngli
        self.progress = QProgressBar()
        self.progress.setFixedHeight(30)
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 3px solid #1565c0;
                border-radius: 15px;
                text-align: center;
                font-weight: bold;
                background: white;
                font-size: 14px;
                color: #1565c0;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #4caf50, stop: 1 #2e7d32);
                border-radius: 12px;
                margin: 2px;
            }
        """)
        
        # Düymələr - daha geniş
        button_layout = QHBoxLayout()
        button_layout.setSpacing(25)
        
        self.scan_btn = QPushButton("🔍 Oxumağa Başla")
        self.scan_btn.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.scan_btn.setFixedSize(200, 55)
        self.scan_btn.clicked.connect(self.start_scanning)
        self.scan_btn.setEnabled(False)
        self.scan_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #1e88e5, stop:1 #1565c0);
                color: white;
                border: none;
                border-radius: 15px;
                padding: 15px 30px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #42a5f5, stop:1 #1e88e5);
                transform: translateY(-2px);
            }
            QPushButton:disabled {
                background: #ccc;
                color: #999;
            }
        """)
        
        cancel_btn = QPushButton("❌ Ləğv et")
        cancel_btn.setFont(QFont("Segoe UI", 14, QFont.Bold))
        cancel_btn.setFixedSize(200, 55)
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #f44336, stop:1 #d32f2f);
                color: white;
                border: none;
                border-radius: 15px;
                padding: 15px 30px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #ef5350, stop:1 #f44336);
                transform: translateY(-2px);
            }
        """)
        
        button_layout.addWidget(self.scan_btn)
        button_layout.addWidget(cancel_btn)
        
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
        self.status_label.setText("Arduino AS608 sensor ilə bağlanılır...\nXahiş edirik səbir edin")
        self.progress.setValue(25)
        
        if self.fingerprint_reader.connect():
            self.status_label.setText("✅ Arduino hazır!\nBarmağınızı sensor üzərinə qoyun və\n'Oxumağa Başla' düyməsinə basın")
            self.progress.setValue(100)
            self.scan_btn.setEnabled(True)
            self.scan_btn.setText("🔍 Barmaq İzi Oxu")
        else:
            self.status_label.setText("⚠️ Arduino tapılmadı\nSimulator rejimi aktivdir\n'Oxumağa Başla' düyməsinə basın")
            self.progress.setValue(50)
            self.scan_btn.setEnabled(True)
            self.scan_btn.setText("🔍 Simulator Test")
        
    def start_scanning(self):
        """Oxuma prosesini başlatma"""
        self.scan_btn.setEnabled(False)
        self.status_label.setText("🔍 Barmaq izi oxunur...\nBarmağınızı yerindən çıxarmayın")
        self.progress.setValue(75)
        
        # Başqa thread-də oxu
        threading.Thread(target=self.scan_fingerprint, daemon=True).start()
        
    def scan_fingerprint(self):
        """Barmaq izi oxuma"""
        try:
            finger_id, message = self.fingerprint_reader.capture_fingerprint()
            
            if finger_id:
                # Pasiyent tapma və ya qeydiyyat
                patient = self.db_manager.find_patient_by_fingerprint(finger_id)
                
                if patient:
                    self.status_label.setText(f"✅ Pasiyent tapıldı!\n{patient['name']} {patient['surname']}")
                    self.progress.setValue(100)
                    
                    # 2 saniyə gözlə və göndər
                    QTimer.singleShot(2000, lambda: self.fingerprint_success.emit(patient))
                    QTimer.singleShot(2500, self.accept)
                else:
                    # Yeni pasiyent qeydiyyatı
                    self.status_label.setText("⚠️ Bu barmaq izi qeydiyyatlı deyil\nYeni pasiyent qeydiyyata alınacaq")
                    self.progress.setValue(75)
                    
                    # Yeni pasiyent yaradılması
                    new_patient = self.create_new_patient(finger_id)
                    if new_patient:
                        QTimer.singleShot(3000, lambda: self.fingerprint_success.emit(new_patient))
                        QTimer.singleShot(3500, self.accept)
                    else:
                        self.reset_scan()
            else:
                self.status_label.setText(f"❌ Oxuma uğursuz:\n{message}")
                self.reset_scan()
                
        except Exception as e:
            self.status_label.setText(f"❌ Xəta baş verdi:\n{str(e)}")
            self.reset_scan()
    
    def create_new_patient(self, finger_id):
        """Yeni pasiyent yaratma"""
        try:
            # Avtomatik pasiyent məlumatları yaratma
            import uuid
            patient_id = f"PAT{uuid.uuid4().hex[:8].upper()}"
            
            patient_data = {
                'id': patient_id,
                'name': f"Pasiyent",
                'surname': f"{finger_id}",
                'birth_date': '1990-01-01',
                'gender': 'K',
                'phone': '+994XXXXXXXXX',
                'address': 'Ünvan qeyd edilməyib',
                'fingerprint_id': str(finger_id),
                'registered_at': datetime.now().isoformat()
            }
            
            # Database-də saxla
            if self.db_manager.create_patient(patient_data):
                self.status_label.setText(f"✅ Yeni pasiyent yaradıldı!\nID: {patient_id}")
                return patient_data
            else:
                self.status_label.setText("❌ Pasiyent yaradılma xətası")
                return None
                
        except Exception as e:
            print(f"Yeni pasiyent yaratma xətası: {e}")
            return None
    
    def reset_scan(self):
        """Oxumanı sıfırla"""
        self.progress.setValue(0)
        self.scan_btn.setEnabled(True)
        self.scan_btn.setText("🔄 Yenidən Cəhd Et")


class PatientPrescriptionHistoryWidget(QWidget):
    """Pasiyent resept tarixçəsi və yeni resept düyməsi"""
    
    new_prescription_requested = pyqtSignal()
    
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.current_patient = None
        self.prescriptions = []
        self.init_ui()
        
    def init_ui(self):
        """UI yaratma"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Pasiyent məlumatları başlığı
        self.patient_info_frame = QFrame()
        self.patient_info_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                          stop:0 #1e88e5, stop:1 #1565c0);
                border-radius: 15px;
                padding: 20px;
                margin: 10px 0;
            }
        """)
        
        patient_layout = QHBoxLayout(self.patient_info_frame)
        
        self.patient_label = QLabel("Pasiyent seçilməyib")
        self.patient_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        self.patient_label.setStyleSheet("color: white;")
        
        patient_layout.addWidget(self.patient_label)
        patient_layout.addStretch()
        
        # Reseptlər tarixçəsi
        history_group = QGroupBox("📋 Resept Tarixçəsi")
        history_group.setFont(QFont("Segoe UI", 14, QFont.Bold))
        history_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e3f2fd;
                border-radius: 15px;
                margin: 15px 0;
                padding: 20px;
                background: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 20px;
                padding: 0 15px;
                color: #1565c0;
                background: white;
            }
        """)
        
        history_layout = QVBoxLayout(history_group)
        
        self.prescriptions_list = QListWidget()
        self.prescriptions_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #e0e0e0;
                border-radius: 10px;
                background: #fafafa;
                padding: 10px;
                font-family: 'Segoe UI';
                font-size: 13px;
            }
            QListWidget::item {
                padding: 15px;
                border-bottom: 1px solid #e0e0e0;
                border-radius: 8px;
                margin: 3px 0;
                background: white;
            }
            QListWidget::item:hover {
                background: #f0f7ff;
            }
            QListWidget::item:selected {
                background: #e3f2fd;
                color: #1565c0;
            }
        """)
        
        history_layout.addWidget(self.prescriptions_list)
        
        # Yeni resept düyməsi
        new_prescription_btn = QPushButton("🏥 Yeni Resept Yaz")
        new_prescription_btn.setFont(QFont("Segoe UI", 16, QFont.Bold))
        new_prescription_btn.setFixedSize(300, 70)
        new_prescription_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #4caf50, stop:1 #388e3c);
                color: white;
                border: none;
                border-radius: 15px;
                padding: 20px;
                font-weight: bold;
                margin: 20px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #66bb6a, stop:1 #4caf50);
                transform: translateY(-3px);
            }
            QPushButton:pressed {
                transform: translateY(0px);
            }
        """)
        new_prescription_btn.clicked.connect(self.new_prescription_requested.emit)
        
        # Düyməni mərkəzləşdir
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(new_prescription_btn)
        button_layout.addStretch()
        
        # Əsas layout-a əlavə et
        main_layout.addWidget(self.patient_info_frame)
        main_layout.addWidget(history_group)
        main_layout.addLayout(button_layout)
        
    def set_patient(self, patient_data):
        """Pasiyent məlumatlarını təyin etmə"""
        self.current_patient = patient_data
        
        # Pasiyent məlumatlarını göstər
        patient_text = f"👤 {patient_data['name']} {patient_data['surname']} | 📱 {patient_data.get('phone', 'N/A')}"
        self.patient_label.setText(patient_text)
        
        # Resept tarixçəsini yüklə
        self.load_prescription_history()
        
    def load_prescription_history(self):
        """Resept tarixçəsini yükləmə"""
        if not self.current_patient:
            return
            
        try:
            prescriptions = self.db_manager.get_patient_prescriptions(self.current_patient['id'])
            self.prescriptions = prescriptions
            
            self.prescriptions_list.clear()
            
            if not prescriptions:
                item = QListWidgetItem("📝 Hələ ki resept yoxdur")
                item.setFont(QFont("Segoe UI", 12))
                self.prescriptions_list.addItem(item)
                return
            
            for prescription in prescriptions:
                date_str = prescription['issued_at'].strftime("%d.%m.%Y %H:%M")
                doctor_name = f"{prescription['doctor_name']} {prescription['doctor_surname']}"
                diagnosis = prescription['diagnosis'][:50] + "..." if len(prescription['diagnosis']) > 50 else prescription['diagnosis']
                
                item_text = f"📅 {date_str} | 👨‍⚕️ Dr. {doctor_name}\n🏥 Diaqnoz: {diagnosis}"
                
                item = QListWidgetItem(item_text)
                item.setFont(QFont("Segoe UI", 11))
                self.prescriptions_list.addItem(item)
                
        except Exception as e:
            print(f"Resept tarixçəsi yükləmə xətası: {e}")


class NewPrescriptionWorkflowWidget(QStackedWidget):
    """Yeni resept workflow - Stack widget ilə mərhələlər"""
    
    workflow_completed = pyqtSignal()
    
    def __init__(self, db_manager, doctor_data):
        super().__init__()
        self.db_manager = db_manager
        self.doctor_data = doctor_data
        self.current_patient = None
        self.init_workflow()
        
    def init_workflow(self):
        """Workflow mərhələlərini yaratma"""
        # 1. Barmaq izi oxuma mərhələsi
        self.fingerprint_dialog = FingerprintFirstDialog(self.db_manager)
        self.fingerprint_dialog.fingerprint_success.connect(self.on_fingerprint_success)
        
        # 2. Pasiyent tarixçəsi mərhələsi  
        self.history_widget = PatientPrescriptionHistoryWidget(self.db_manager)
        self.history_widget.new_prescription_requested.connect(self.start_new_prescription)
        self.addWidget(self.history_widget)
        
        # 3. Yeni resept yazma mərhələsi
        from ui.prescription_workflow import NewPrescriptionWidget  # Import edəcəyik
        self.prescription_widget = NewPrescriptionWidget(self.db_manager, self.doctor_data)
        self.addWidget(self.prescription_widget)
        
    def start_workflow(self):
        """Workflow-u başlatma"""
        # İlk öncə barmaq izi oxuma
        self.fingerprint_dialog.exec_()
        
    def on_fingerprint_success(self, patient_data):
        """Barmaq izi uğurlu oxunduqda"""
        self.current_patient = patient_data
        
        # Pasiyent tarixçəsi mərhələsinə keç
        self.history_widget.set_patient(patient_data)
        self.setCurrentWidget(self.history_widget)
        
    def start_new_prescription(self):
        """Yeni resept yazma mərhələsinə keçmə"""
        if self.current_patient:
            self.prescription_widget.set_patient(self.current_patient)
            self.setCurrentWidget(self.prescription_widget)