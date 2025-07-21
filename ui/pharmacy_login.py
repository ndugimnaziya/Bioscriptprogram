#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QLineEdit, QPushButton, QMessageBox, QApplication)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette, QBrush, QLinearGradient, QColor
from database.connection import DatabaseConnection
from ui.pharmacy_dashboard import PharmacyDashboard

class PharmacyLoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = DatabaseConnection()
        self.init_ui()
        
    def init_ui(self):
        """UI-ni hazırla"""
        self.setWindowTitle("BioScript Aptek Sistemi - Giriş")
        self.setGeometry(100, 100, 800, 600)
        
        # Tam ekran etmək üçün
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.showFullScreen()
        
        # Ana widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Gradient arxa fon
        self.set_gradient_background()
        
        # Ana layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setSpacing(30)
        
        # Logo (BioScript)
        logo_label = QLabel("🏥 BioScript")
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setFont(QFont("Segoe UI", 48, QFont.Bold))
        logo_label.setStyleSheet("""
            color: white;
            background: transparent;
            margin: 20px;
        """)
        main_layout.addWidget(logo_label)
        
        # Alt başlıq
        subtitle_label = QLabel("Aptek İdarəetmə Sistemi")
        subtitle_label.setAlignment(Qt.AlignCenter) 
        subtitle_label.setFont(QFont("Segoe UI", 18))
        subtitle_label.setStyleSheet("""
            color: #E3F2FD;
            background: transparent;
            margin-bottom: 30px;
        """)
        main_layout.addWidget(subtitle_label)
        
        # Giriş formu
        self.create_login_form(main_layout)
        
        # ESC ilə çıxış
        self.setFocusPolicy(Qt.StrongFocus)
        
    def set_gradient_background(self):
        """Gradient arxa fon təyin et"""
        palette = self.palette()
        gradient = QLinearGradient(0, 0, 0, 1)
        gradient.setCoordinateMode(QLinearGradient.ObjectBoundingMode)
        gradient.setColorAt(0, QColor(25, 118, 210))  # Mavi
        gradient.setColorAt(1, QColor(13, 71, 161))   # Tünd mavi
        palette.setBrush(QPalette.Window, QBrush(gradient))
        self.setPalette(palette)
        
    def create_login_form(self, main_layout):
        """Giriş formunu yarat"""
        # Form container
        form_widget = QWidget()
        form_widget.setFixedSize(400, 300)
        form_widget.setStyleSheet("""
            QWidget {
                background: rgba(255, 255, 255, 0.9);
                border-radius: 15px;
                padding: 20px;
            }
        """)
        
        form_layout = QVBoxLayout(form_widget)
        form_layout.setSpacing(20)
        form_layout.setContentsMargins(30, 30, 30, 30)
        
        # İstifadəçi adı
        username_label = QLabel("İstifadəçi Adı:")
        username_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        username_label.setStyleSheet("color: #1976D2; background: transparent;")
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Aptek istifadəçi adını daxil edin")
        self.username_input.setFont(QFont("Segoe UI", 11))
        self.username_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 2px solid #E3F2FD;
                border-radius: 8px;
                background: white;
                font-size: 11pt;
            }
            QLineEdit:focus {
                border-color: #1976D2;
            }
        """)
        
        # Şifrə
        password_label = QLabel("Şifrə:")
        password_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        password_label.setStyleSheet("color: #1976D2; background: transparent;")
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Şifrəni daxil edin")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFont(QFont("Segoe UI", 11))
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 2px solid #E3F2FD;
                border-radius: 8px;
                background: white;
                font-size: 11pt;
            }
            QLineEdit:focus {
                border-color: #1976D2;
            }
        """)
        
        # Giriş düyməsi
        login_button = QPushButton("GİRİŞ")
        login_button.setFont(QFont("Segoe UI", 12, QFont.Bold))
        login_button.setFixedHeight(45)
        login_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2196F3, stop:1 #1976D2);
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 12pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #42A5F5, stop:1 #2196F3);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1976D2, stop:1 #1565C0);
            }
        """)
        login_button.clicked.connect(self.login)
        
        # Çıxış düyməsi
        exit_button = QPushButton("ÇIXIŞ (ESC)")
        exit_button.setFont(QFont("Segoe UI", 10))
        exit_button.setFixedHeight(35)
        exit_button.setStyleSheet("""
            QPushButton {
                background: rgba(244, 67, 54, 0.8);
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 10pt;
            }
            QPushButton:hover {
                background: rgba(244, 67, 54, 1);
            }
        """)
        exit_button.clicked.connect(self.close)
        
        # Form elementlərini əlavə et
        form_layout.addWidget(username_label)
        form_layout.addWidget(self.username_input)
        form_layout.addWidget(password_label)
        form_layout.addWidget(self.password_input)
        form_layout.addWidget(login_button)
        form_layout.addWidget(exit_button)
        
        main_layout.addWidget(form_widget, 0, Qt.AlignCenter)
        
        # Enter düyməsi ilə giriş
        self.password_input.returnPressed.connect(self.login)
        
    def keyPressEvent(self, event):
        """Klaviatura hadisələri"""
        if event.key() == Qt.Key_Escape:
            self.close()
        super().keyPressEvent(event)
        
    def login(self):
        """Giriş prosedurunun aparılması"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not username or not password:
            QMessageBox.warning(self, "Xəta", "Bütün sahələri doldurun!")
            return
            
        # Verilənlər bazasına qoşul
        if not self.db.connect():
            QMessageBox.critical(self, "Xəta", "Verilənlər bazasına qoşula bilmədi!")
            return
            
        # Aptek personalını yoxla
        query = """
            SELECT ps.*, p.name as pharmacy_name, p.id as pharmacy_id,
                   p.current_month_commission, p.commission_rate
            FROM pharmacy_staff ps
            JOIN pharmacies p ON ps.pharmacy_id = p.id
            WHERE ps.username = %s AND ps.password = %s AND ps.is_active = 1
        """
        
        result = self.db.execute_query(query, (username, password))
        
        if result and len(result) > 0:
            user_data = result[0]
            
            # Uğurlu giriş - Dashboard-a get
            self.hide()
            self.dashboard = PharmacyDashboard(user_data, self.db)
            self.dashboard.show()
            
        else:
            QMessageBox.warning(self, "Giriş Xətası", 
                              "İstifadəçi adı və ya şifrə yanlışdır!")
                              
        self.db.disconnect()