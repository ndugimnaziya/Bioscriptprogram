#!/usr/bin/env python3
"""
BioScript - Sadə Həkim Giriş Ekranı
Çox sadə və təmiz dizayn
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QFrame, QWidget)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap
import os

class NewDoctorLoginWindow(QDialog):
    """Sadə həkim giriş pəncərəsi"""
    
    login_successful = pyqtSignal(dict)
    
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.init_ui()
        
    def init_ui(self):
        """Tam ekran interfeys yaratma"""
        self.setWindowTitle("BioScript - Həkim Girişi")
        
        # Həqiqi tam ekran - pəncərə çərçivəsiz
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.showFullScreen()  # Tam ekran
        self.setModal(True)
        
        # Ana layout - tam ekran üçün
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Mərkəz container
        center_widget = QWidget()
        center_layout = QVBoxLayout(center_widget)
        center_layout.setAlignment(Qt.AlignCenter)
        center_layout.setContentsMargins(80, 60, 80, 60)
        center_layout.setSpacing(40)
        
        # Logo
        self.create_logo_section(center_layout)
        
        # Giriş formu
        self.create_login_form(center_layout)
        
        # Mərkəz widget-i ana layout-a əlavə et
        main_layout.addWidget(center_widget)
        
        # Stil tətbiq et
        self.apply_simple_style()
        
    def create_logo_section(self, layout):
        """Logo bölməsi yaratma"""
        logo_frame = QFrame()
        logo_layout = QVBoxLayout(logo_frame)
        logo_layout.setSpacing(25)
        logo_layout.setAlignment(Qt.AlignCenter)
        
        # Original BioScript logosu
        try:
            logo_label = QLabel()
            pixmap = QPixmap("static/bioscript_logo_original.png")
            if not pixmap.isNull():
                # Logo ölçüsünü kiçilt (450x180 maksimum)
                scaled_pixmap = pixmap.scaled(450, 180, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                logo_label.setPixmap(scaled_pixmap)
                logo_label.setAlignment(Qt.AlignCenter)
                logo_label.setStyleSheet("background: transparent; margin-bottom: 20px;")
                logo_layout.addWidget(logo_label)
            else:
                raise Exception("Logo yüklənmədi")
        except Exception as e:
            # Fallback - sadə mətn logosu
            print(f"Logo yüklənmə xətası: {e}")
            logo_text = QLabel("BioScript")
            logo_text.setFont(QFont("Arial", 36, QFont.Bold))
            logo_text.setAlignment(Qt.AlignCenter)
            logo_text.setStyleSheet("color: #1e88e5; background: transparent;")
            logo_layout.addWidget(logo_text)
        
        # Sloqan - orta ölçü
        slogan = QLabel("Səhiyyə Barmaqlarınızın Ucundadır!")
        slogan.setFont(QFont("Arial", 18))
        slogan.setAlignment(Qt.AlignCenter)
        slogan.setStyleSheet("color: #555; font-style: italic; margin-top: 20px; margin-bottom: 40px;")
        logo_layout.addWidget(slogan)
        
        layout.addWidget(logo_frame)
        
    def create_login_form(self, layout):
        """Giriş formu yaratma"""
        form_frame = QFrame()
        form_frame.setObjectName("loginForm")
        form_frame.setFixedWidth(550)  # Sabit genişlik artırıldı
        form_frame.setMaximumHeight(500)  # Maksimum yüksəklik artırıldı
        form_layout = QVBoxLayout(form_frame)
        form_layout.setSpacing(30)
        form_layout.setContentsMargins(50, 45, 50, 45)
        
        # Başlıq - orta ölçü
        title = QLabel("Həkim Girişi")
        title.setFont(QFont("Arial", 22, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #333; margin-bottom: 25px; background: transparent;")
        form_layout.addWidget(title)
        
        # Boşluq
        form_layout.addSpacing(15)
        
        # İstifadəçi adı
        username_label = QLabel("İstifadəçi adı:")
        username_label.setFont(QFont("Arial", 14, QFont.Bold))
        username_label.setStyleSheet("color: #555; margin-bottom: 5px;")
        form_layout.addWidget(username_label)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("İstifadəçi adınızı daxil edin")
        self.username_input.setFont(QFont("Arial", 14))
        self.username_input.setFixedHeight(55)
        form_layout.addWidget(self.username_input)
        
        # Boşluq
        form_layout.addSpacing(10)
        
        # Şifrə
        password_label = QLabel("Şifrə:")
        password_label.setFont(QFont("Arial", 14, QFont.Bold))
        password_label.setStyleSheet("color: #555; margin-bottom: 5px;")
        form_layout.addWidget(password_label)
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Şifrənizi daxil edin")
        self.password_input.setFont(QFont("Arial", 14))
        self.password_input.setFixedHeight(55)
        form_layout.addWidget(self.password_input)
        
        # Boşluq
        form_layout.addSpacing(20)
        
        # Düymələr container
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)
        
        # Çıxış düyməsi (Esc)
        exit_btn = QPushButton("ÇIXIŞ (ESC)")
        exit_btn.setFont(QFont("Arial", 12))
        exit_btn.setFixedHeight(45)
        exit_btn.setStyleSheet("""
            QPushButton {
                background: #f44336;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #d32f2f;
            }
        """)
        exit_btn.clicked.connect(self.close)
        buttons_layout.addWidget(exit_btn)
        
        buttons_layout.addStretch()  # Boşluq
        
        # Giriş düyməsi
        self.login_button = QPushButton("GİRİŞ")
        self.login_button.setFont(QFont("Arial", 16, QFont.Bold))
        self.login_button.setFixedHeight(55)
        self.login_button.clicked.connect(self.handle_login)
        buttons_layout.addWidget(self.login_button)
        
        form_layout.addLayout(buttons_layout)
        
        # Keyboard shortcut-lar
        self.username_input.returnPressed.connect(self.handle_login)
        self.password_input.returnPressed.connect(self.handle_login)
        
        # ESC açarı ilə çıxış
        self.setFocusPolicy(Qt.StrongFocus)
        self.installEventFilter(self)
        
        layout.addWidget(form_frame)
        
    def apply_simple_style(self):
        """Sadə stil tətbiq etmə"""
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #e3f2fd, stop:0.3 #f0f8ff, 
                                          stop:0.7 #f8f9fa, stop:1 #e1f5fe);
            }
            
            QFrame#loginForm {
                background: rgba(255, 255, 255, 0.95);
                border: 2px solid #e3f2fd;
                border-radius: 15px;
                padding: 25px;
                margin-top: 15px;
            }
            
            QLineEdit {
                border: 2px solid #ddd;
                border-radius: 8px;
                padding: 15px;
                font-size: 14px;
                background: white;
                margin-top: 5px;
                margin-bottom: 10px;
            }
            
            QLineEdit:focus {
                border-color: #1e88e5;
                outline: none;
                background: #f0f8ff;
            }
            
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #1e88e5, stop:1 #1976d2);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 15px;
                font-size: 16px;
                font-weight: bold;
                margin-top: 15px;
            }
            
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #1976d2, stop:1 #1565c0);
            }
            
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #1565c0, stop:1 #0d47a1);
            }
        """)
        
    def eventFilter(self, obj, event):
        """Event filter - ESC açarı ilə çıxış"""
        if event.type() == event.KeyPress and event.key() == Qt.Key_Escape:
            self.close()
            return True
        return super().eventFilter(obj, event)
        
    def handle_login(self):
        """Giriş idarəetməsi"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not username or not password:
            self.show_error("İstifadəçi adı və şifrə tələb olunur!")
            return
            
        # Verilənlər bazası ilə yoxlama
        doctor_data = self.db_manager.authenticate_doctor(username, password)
        
        if doctor_data:
            self.login_successful.emit(doctor_data)
            self.accept()
        else:
            self.show_error("Yanlış istifadəçi adı və ya şifrə!")
            
    def show_error(self, message):
        """Xəta mesajı göstərmə"""
        from PyQt5.QtWidgets import QMessageBox
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Giriş Xətası")
        msg.setText(message)
        msg.setStyleSheet("QMessageBox { background: white; }")
        msg.exec_()