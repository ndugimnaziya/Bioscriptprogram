"""
BioScript - Həkim Giriş Pəncərəsi
Həkim autentifikasiya interfeysi
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QFormLayout, QFrame,
                            QMessageBox, QCheckBox, QProgressBar)
from PyQt5.QtCore import Qt, pyqtSignal, QThread, pyqtSignal as Signal
from PyQt5.QtGui import QFont, QPixmap, QIcon

class LoginThread(QThread):
    """Giriş thread sinifi"""
    login_result = Signal(bool, dict)
    
    def __init__(self, db_manager, username, password):
        super().__init__()
        self.db_manager = db_manager
        self.username = username
        self.password = password
    
    def run(self):
        try:
            doctor_data = self.db_manager.authenticate_doctor(self.username, self.password)
            if doctor_data:
                self.login_result.emit(True, doctor_data)
            else:
                self.login_result.emit(False, {})
        except Exception as e:
            print(f"Giriş thread xətası: {e}")
            self.login_result.emit(False, {})

class DoctorLoginWindow(QDialog):
    """Həkim giriş pəncərəsi"""
    
    login_successful = pyqtSignal(dict)
    
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.login_thread = None
        
        self.init_ui()
        self.apply_style()
    
    def init_ui(self):
        """İstifadəçi interfeysi başlatma"""
        self.setWindowTitle("BioScript - Həkim Girişi")
        self.setFixedSize(400, 300)
        self.setModal(True)
        
        # Ana layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        
        # Header
        self.create_header(main_layout)
        
        # Giriş formu
        self.create_login_form(main_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        # Düymələr
        self.create_buttons(main_layout)
    
    def create_header(self, parent_layout):
        """Header yaratma"""
        header_frame = QFrame()
        header_layout = QVBoxLayout(header_frame)
        
        # Logo və başlıq
        title_label = QLabel("🏥 BioScript")
        title_label.setFont(QFont("Arial", 28, QFont.Bold))
        title_label.setAlignment(Qt.AlignHCenter)
        title_label.setStyleSheet("color: #2c3e50; margin: 20px;")
        
        subtitle_label = QLabel("Tibbi Resept İdarəetmə Sistemi")
        subtitle_label.setFont(QFont("Arial", 12))
        subtitle_label.setAlignment(Qt.AlignHCenter)
        subtitle_label.setStyleSheet("color: #7f8c8d; margin-bottom: 10px;")
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        
        parent_layout.addWidget(header_frame)
    
    def create_login_form(self, parent_layout):
        """Giriş formu yaratma"""
        form_frame = QFrame()
        form_frame.setFrameStyle(QFrame.Box)
        form_frame.setStyleSheet("QFrame { border: 1px solid #bdc3c7; border-radius: 8px; padding: 10px; }")
        
        form_layout = QFormLayout(form_frame)
        form_layout.setSpacing(15)
        
        # İstifadəçi adı
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("İstifadəçi adınızı daxil edin")
        self.username_input.setText("hekim1")  # Test üçün
        form_layout.addRow("İstifadəçi adı:", self.username_input)
        
        # Şifrə
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Şifrənizi daxil edin")
        self.password_input.setText("123456")  # Test üçün
        form_layout.addRow("Şifrə:", self.password_input)
        
        # Şifrəni yadda saxla
        self.remember_checkbox = QCheckBox("Şifrəni yadda saxla")
        form_layout.addRow("", self.remember_checkbox)
        
        # Enter düyməsi ilə giriş
        self.password_input.returnPressed.connect(self.login)
        self.username_input.returnPressed.connect(self.login)
        
        parent_layout.addWidget(form_frame)
    
    def create_buttons(self, parent_layout):
        """Düymələr yaratma"""
        button_layout = QHBoxLayout()
        
        # Giriş düyməsi
        self.login_button = QPushButton("Giriş")
        self.login_button.setDefault(True)
        self.login_button.clicked.connect(self.login)
        
        # Ləğv düyməsi
        cancel_button = QPushButton("Ləğv et")
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(self.login_button)
        
        parent_layout.addLayout(button_layout)
    
    def apply_style(self):
        """Stil tətbiq etmə"""
        style = """
        QDialog {
            background-color: #f8f9fa;
        }
        
        QLineEdit {
            border: 2px solid #e9ecef;
            border-radius: 6px;
            padding: 10px;
            font-size: 14px;
            background-color: white;
        }
        
        QLineEdit:focus {
            border-color: #007bff;
        }
        
        QPushButton {
            background-color: #007bff;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 6px;
            font-weight: bold;
            font-size: 14px;
            min-width: 100px;
        }
        
        QPushButton:hover {
            background-color: #0056b3;
        }
        
        QPushButton:pressed {
            background-color: #004085;
        }
        
        QPushButton:default {
            background-color: #28a745;
        }
        
        QPushButton:default:hover {
            background-color: #218838;
        }
        
        QCheckBox {
            font-size: 12px;
            color: #6c757d;
        }
        
        QProgressBar {
            border: 2px solid #e9ecef;
            border-radius: 6px;
            text-align: center;
            background-color: #f8f9fa;
        }
        
        QProgressBar::chunk {
            background-color: #007bff;
            border-radius: 4px;
        }
        """
        
        self.setStyleSheet(style)
    
    def login(self):
        """Giriş əməliyyatı"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        # Validasiya
        if not username:
            QMessageBox.warning(self, "Xəta", "İstifadəçi adını daxil edin!")
            self.username_input.setFocus()
            return
        
        if not password:
            QMessageBox.warning(self, "Xəta", "Şifrəni daxil edin!")
            self.password_input.setFocus()
            return
        
        # UI bloklama
        self.set_login_in_progress(True)
        
        # Giriş thread başlatma
        self.login_thread = LoginThread(self.db_manager, username, password)
        self.login_thread.login_result.connect(self.on_login_result)
        self.login_thread.start()
    
    def on_login_result(self, success, doctor_data):
        """Giriş nəticəsi"""
        self.set_login_in_progress(False)
        
        if success:
            # Uğurlu giriş
            QMessageBox.information(self, "Uğur", 
                                  f"Xoş gəlmisiniz, Dr. {doctor_data['name']} {doctor_data['surname']}!")
            
            self.login_successful.emit(doctor_data)
            self.accept()
        else:
            # Uğursuz giriş
            QMessageBox.critical(self, "Xəta", 
                               "İstifadəçi adı və ya şifrə yanlışdır!\n\n"
                               "Test məlumatları:\n"
                               "İstifadəçi adı: hekim1\n"
                               "Şifrə: 123456")
            
            self.password_input.clear()
            self.password_input.setFocus()
    
    def set_login_in_progress(self, in_progress):
        """Giriş prosesi göstəricisi"""
        self.login_button.setEnabled(not in_progress)
        self.username_input.setEnabled(not in_progress)
        self.password_input.setEnabled(not in_progress)
        
        if in_progress:
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # Indeterminate progress
            self.login_button.setText("Giriş edilir...")
        else:
            self.progress_bar.setVisible(False)
            self.login_button.setText("Giriş")
    
    def keyPressEvent(self, event):
        """Klaviatura hadisələri"""
        if event.key() == 16777216:  # Qt.Key_Escape
            self.reject()
        else:
            super().keyPressEvent(event)