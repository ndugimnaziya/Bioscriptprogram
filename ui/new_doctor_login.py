#!/usr/bin/env python3
"""
BioScript - Sadə Həkim Giriş Ekranı
Çox sadə və təmiz dizayn
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QFrame, QWidget)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtSvg import QSvgWidget
import os

class NewDoctorLoginWindow(QDialog):
    """Sadə həkim giriş pəncərəsi"""
    
    login_successful = pyqtSignal(dict)
    
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.init_ui()
        
    def init_ui(self):
        """Sadə interfeys yaratma"""
        self.setWindowTitle("BioScript - Həkim Girişi")
        self.setFixedSize(500, 600)
        self.setModal(True)
        
        # Pəncərəni mərkəzləşdir
        self.move(
            (self.screen().geometry().width() - self.width()) // 2,
            (self.screen().geometry().height() - self.height()) // 2
        )
        
        # Ana layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(30)
        
        # Logo
        self.create_logo_section(main_layout)
        
        # Giriş formu
        self.create_login_form(main_layout)
        
        # Stil tətbiq et
        self.apply_simple_style()
        
    def create_logo_section(self, layout):
        """Logo bölməsi yaratma"""
        logo_frame = QFrame()
        logo_layout = QVBoxLayout(logo_frame)
        logo_layout.setSpacing(20)
        logo_layout.setAlignment(Qt.AlignCenter)
        
        # SVG logo
        try:
            logo_svg = QSvgWidget("static/bioscript_simple_logo.svg")
            logo_svg.setFixedSize(400, 100)
            logo_layout.addWidget(logo_svg)
        except:
            # Fallback - sadə mətn logosu
            logo_text = QLabel("BioScript")
            logo_text.setFont(QFont("Arial", 36, QFont.Bold))
            logo_text.setAlignment(Qt.AlignCenter)
            logo_text.setStyleSheet("color: #1e88e5;")
            logo_layout.addWidget(logo_text)
        
        # Sloqan
        slogan = QLabel("Səhiyyə Barmaqlarınızın Ucundadır!")
        slogan.setFont(QFont("Arial", 14))
        slogan.setAlignment(Qt.AlignCenter)
        slogan.setStyleSheet("color: #666; font-style: italic;")
        logo_layout.addWidget(slogan)
        
        layout.addWidget(logo_frame)
        
    def create_login_form(self, layout):
        """Giriş formu yaratma"""
        form_frame = QFrame()
        form_frame.setObjectName("loginForm")
        form_layout = QVBoxLayout(form_frame)
        form_layout.setSpacing(20)
        
        # Başlıq
        title = QLabel("Həkim Girişi")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #333; margin-bottom: 10px;")
        form_layout.addWidget(title)
        
        # İstifadəçi adı
        username_label = QLabel("İstifadəçi adı:")
        username_label.setFont(QFont("Arial", 12))
        username_label.setStyleSheet("color: #666;")
        form_layout.addWidget(username_label)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("İstifadəçi adınızı daxil edin")
        self.username_input.setFont(QFont("Arial", 14))
        self.username_input.setFixedHeight(50)
        form_layout.addWidget(self.username_input)
        
        # Şifrə
        password_label = QLabel("Şifrə:")
        password_label.setFont(QFont("Arial", 12))
        password_label.setStyleSheet("color: #666;")
        form_layout.addWidget(password_label)
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Şifrənizi daxil edin")
        self.password_input.setFont(QFont("Arial", 14))
        self.password_input.setFixedHeight(50)
        form_layout.addWidget(self.password_input)
        
        # Giriş düyməsi
        self.login_button = QPushButton("GİRİŞ")
        self.login_button.setFont(QFont("Arial", 14, QFont.Bold))
        self.login_button.setFixedHeight(50)
        self.login_button.clicked.connect(self.handle_login)
        form_layout.addWidget(self.login_button)
        
        # Enter basıldıqda giriş
        self.username_input.returnPressed.connect(self.handle_login)
        self.password_input.returnPressed.connect(self.handle_login)
        
        layout.addWidget(form_frame)
        
    def apply_simple_style(self):
        """Sadə stil tətbiq etmə"""
        self.setStyleSheet("""
            QDialog {
                background: white;
            }
            
            QFrame#loginForm {
                background: #f8f9fa;
                border: 2px solid #e3f2fd;
                border-radius: 15px;
                padding: 30px;
            }
            
            QLineEdit {
                border: 2px solid #ddd;
                border-radius: 8px;
                padding: 15px;
                font-size: 14px;
                background: white;
            }
            
            QLineEdit:focus {
                border-color: #1e88e5;
                outline: none;
            }
            
            QPushButton {
                background: #1e88e5;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 15px;
                font-size: 14px;
                font-weight: bold;
            }
            
            QPushButton:hover {
                background: #1976d2;
            }
            
            QPushButton:pressed {
                background: #1565c0;
            }
        """)
        
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