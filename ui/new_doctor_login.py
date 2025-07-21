#!/usr/bin/env python3
"""
BioScript - Yeni Həkim Giriş Ekranı
Tam ekran, modern dizayn
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QFrame, QWidget,
                            QGraphicsDropShadowEffect, QSpacerItem, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QPixmap, QPainter, QColor, QPalette

class NewDoctorLoginWindow(QDialog):
    """Yeni tam ekran həkim giriş pəncərəsi"""
    
    login_successful = pyqtSignal(dict)
    
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.init_ui()
        self.apply_style()
        
    def init_ui(self):
        """İnterfeys yaratma"""
        self.setWindowTitle("BioScript - Həkim Girişi")
        self.showMaximized()
        self.setModal(True)
        
        # Ana layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Arxa fon
        self.create_background(main_layout)
        
        # Mərkəz giriş paneli
        self.create_login_panel(main_layout)
        
    def create_background(self, parent_layout):
        """Arxa fon və header yaratma"""
        # Header container
        header_frame = QFrame()
        header_frame.setFixedHeight(120)
        header_frame.setObjectName("headerFrame")
        
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(50, 20, 50, 20)
        
        # Logo və başlıq
        logo_widget = QWidget()
        logo_layout = QHBoxLayout(logo_widget)
        logo_layout.setSpacing(20)
        
        # Logo (BioScript barmaq izi)
        logo_label = QLabel("👆")
        logo_label.setFont(QFont("Arial", 60))
        logo_label.setStyleSheet("color: #42a5f5; margin: 0px;")
        
        # Başlıq və sloqan
        title_widget = QWidget()
        title_layout = QVBoxLayout(title_widget)
        title_layout.setSpacing(5)
        title_layout.setContentsMargins(0, 0, 0, 0)
        
        title_label = QLabel("BioScript")
        title_label.setFont(QFont("Arial", 48, QFont.Bold))
        title_label.setStyleSheet("color: #1e88e5; margin: 0px;")
        
        slogan_label = QLabel("Səhiyyə Barmaqlarınızın Ucundadır!")
        slogan_font = QFont("Arial", 16)
        slogan_font.setItalic(True)
        slogan_label.setFont(slogan_font)
        slogan_label.setStyleSheet("color: #1976d2; margin: 0px;")
        
        title_layout.addWidget(title_label)
        title_layout.addWidget(slogan_label)
        
        logo_layout.addWidget(logo_label)
        logo_layout.addWidget(title_widget)
        logo_layout.addStretch()
        
        header_layout.addWidget(logo_widget)
        parent_layout.addWidget(header_frame)
        
    def create_login_panel(self, parent_layout):
        """Giriş paneli yaratma"""
        # Mərkəz container
        center_frame = QFrame()
        center_layout = QHBoxLayout(center_frame)
        center_layout.setContentsMargins(50, 100, 50, 100)
        
        # Sol boşluq
        center_layout.addStretch(2)
        
        # Giriş paneli
        login_frame = QFrame()
        login_frame.setFixedSize(450, 350)
        login_frame.setObjectName("loginFrame")
        
        # Gölgə effekti
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(30, 136, 229, 100))
        shadow.setOffset(0, 10)
        login_frame.setGraphicsEffect(shadow)
        
        login_layout = QVBoxLayout(login_frame)
        login_layout.setContentsMargins(40, 40, 40, 40)
        login_layout.setSpacing(20)
        
        # Panel başlığı - Professional
        panel_title = QLabel("🩺 HƏKİM GİRİŞ SİSTEMİ")
        panel_title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        panel_title.setAlignment(Qt.AlignCenter)
        panel_title.setStyleSheet("color: #1e88e5; margin-bottom: 15px; letter-spacing: 1px;")
        
        # İstifadəçi adı - Professional
        username_label = QLabel("👨‍⚕️ Həkim İstifadəçi Adı:")
        username_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        username_label.setStyleSheet("color: #1565c0; margin-top: 10px;")
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Həkim lisenziya ID-nizi daxil edin")
        self.username_input.setFixedHeight(45)
        self.username_input.setText("huseyn")  # Test üçün
        
        # Şifrə - Professional
        password_label = QLabel("🔐 Təhlükəsizlik Şifrəsi:")
        password_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        password_label.setStyleSheet("color: #1565c0;")
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Təhlükəsizlik şifrənizi daxil edin")
        self.password_input.setFixedHeight(45)
        self.password_input.setText("huseyn")  # Test üçün
        
        # Professional düymələr
        login_btn = QPushButton("🚀 SİSTEMƏ GİR")
        login_btn.setFixedHeight(55)
        login_btn.setFont(QFont("Segoe UI", 14, QFont.Bold))
        login_btn.clicked.connect(self.login)
        login_btn.setObjectName("loginButton")
        
        cancel_btn = QPushButton("❌ LƏĞV ET")
        cancel_btn.setFixedHeight(45)
        cancel_btn.setFont(QFont("Segoe UI", 12))
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setObjectName("cancelButton")
        
        # Layout-a əlavə etmə
        login_layout.addWidget(panel_title)
        login_layout.addWidget(username_label)
        login_layout.addWidget(self.username_input)
        login_layout.addWidget(password_label)
        login_layout.addWidget(self.password_input)
        login_layout.addSpacing(10)
        login_layout.addWidget(login_btn)
        login_layout.addWidget(cancel_btn)
        
        center_layout.addWidget(login_frame)
        
        # Sağ boşluq
        center_layout.addStretch(2)
        
        parent_layout.addWidget(center_frame)
        
        # Enter key ilə giriş
        self.username_input.returnPressed.connect(self.login)
        self.password_input.returnPressed.connect(self.login)
        
    def login(self):
        """Həkim girişi"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not username or not password:
            self.show_error("İstifadəçi adı və şifrə daxil edin!")
            return
        
        # Verilənlər bazası yoxlaması
        doctor = self.db_manager.authenticate_doctor(username, password)
        
        if doctor:
            self.login_successful.emit(doctor)
            self.accept()
        else:
            self.show_error("İstifadəçi adı və ya şifrə yanlışdır!")
    
    def show_error(self, message):
        """Xəta mesajı göstərmə"""
        error_label = QLabel(message)
        error_label.setStyleSheet("""
            QLabel {
                color: #d32f2f;
                background-color: #ffebee;
                border: 1px solid #f8bbd9;
                border-radius: 4px;
                padding: 8px;
                font-weight: bold;
            }
        """)
        error_label.setAlignment(Qt.AlignCenter)
        
        # Animasiya ilə göstərmə
        # Sadəlik üçün hal-hazırda statusBar mesajı
        print(f"⚠️ {message}")
        
    def apply_style(self):
        """Stil tətbiqi"""
        style = """
        QDialog {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                      stop:0 #e3f2fd, stop:0.5 #bbdefb, stop:1 #90caf9);
        }
        
        QFrame#headerFrame {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                      stop:0 #1e88e5, stop:1 #1976d2);
            border: none;
        }
        
        QFrame#loginFrame {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                      stop:0 #ffffff, stop:1 #f5f5f5);
            border: 2px solid #1e88e5;
            border-radius: 15px;
        }
        
        QLineEdit {
            border: 2px solid #90caf9;
            border-radius: 8px;
            padding: 10px 15px;
            font-size: 14px;
            background-color: white;
        }
        
        QLineEdit:focus {
            border-color: #1e88e5;
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                      stop:0 #ffffff, stop:1 #f0f8ff);
        }
        
        QPushButton#loginButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                      stop:0 #1e88e5, stop:1 #1976d2);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
        }
        
        QPushButton#loginButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                      stop:0 #1976d2, stop:1 #1565c0);
        }
        
        QPushButton#loginButton:pressed {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                      stop:0 #1565c0, stop:1 #0d47a1);
        }
        
        QPushButton#cancelButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                      stop:0 #fafafa, stop:1 #e0e0e0);
            color: #424242;
            border: 1px solid #bdbdbd;
            border-radius: 6px;
        }
        
        QPushButton#cancelButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                      stop:0 #f5f5f5, stop:1 #eeeeee);
        }
        """
        
        self.setStyleSheet(style)