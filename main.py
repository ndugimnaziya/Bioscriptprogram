#!/usr/bin/env python3
"""
BioScript - Tibbi Resept İdarəetmə Sistemi
Əsas aplikasiya faylı
"""

import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                            QTabWidget, QTableWidget, QTableWidgetItem,
                            QTextEdit, QComboBox, QDateEdit, QMessageBox,
                            QSplitter, QFrame, QGridLayout, QScrollArea,
                            QGroupBox, QSpinBox, QFormLayout)
from PyQt5.QtCore import Qt, QDate, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QPalette, QColor, QPixmap

from database.db_manager import DatabaseManager
from ui.doctor_login import DoctorLoginWindow
from ui.patient_search import PatientSearchWidget
from ui.prescription_editor import PrescriptionEditorWidget
from ui.statistics_dashboard import StatisticsDashboard

class BioScriptMainWindow(QMainWindow):
    """Əsas aplikasiya pəncərəsi"""
    
    def __init__(self):
        super().__init__()
        self.db_manager = DatabaseManager()
        self.current_doctor = None
        self.current_patient = None
        
        # Dizayn və görünüş
        self.init_ui()
        self.apply_style()
        
        # Giriş pəncərəsini göstər
        self.show_login()
    
    def init_ui(self):
        """İstifadəçi interfeysi başlatma"""
        self.setWindowTitle("BioScript - Səhiyyə Barmaqlarınızın Ucundadır!")
        self.showMaximized()  # Tam ekran açılsın
        
        # Mərkəzi widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Əsas layout
        main_layout = QVBoxLayout(central_widget)
        
        # Header
        self.create_header(main_layout)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Tablar
        self.create_tabs()
        
        # Status bar
        self.statusBar().showMessage("Hazır")
    
    def create_header(self, parent_layout):
        """Header hissəsini yaratma"""
        header_frame = QFrame()
        header_frame.setFrameStyle(QFrame.Box)
        header_frame.setMaximumHeight(80)
        
        header_layout = QHBoxLayout(header_frame)
        
        # Logo və başlıq
        title_widget = QWidget()
        title_layout = QHBoxLayout(title_widget)
        title_layout.setSpacing(15)
        title_layout.setContentsMargins(10, 5, 10, 5)
        
        # Logo (fingerprint emoji BioScript temasına uyğun)
        logo_label = QLabel("👆")
        logo_label.setFont(QFont("Arial", 48))
        logo_label.setStyleSheet("margin: 0px; padding: 5px;")
        title_layout.addWidget(logo_label)
        
        # Başlıq və sloqan
        text_widget = QWidget()
        text_layout = QVBoxLayout(text_widget)
        text_layout.setSpacing(2)
        text_layout.setContentsMargins(0, 0, 0, 0)
        
        # Ana başlıq
        title_label = QLabel("BioScript")
        title_label.setFont(QFont("Arial", 28, QFont.Bold))
        title_label.setStyleSheet("color: #1e88e5; margin: 0px;")
        
        # Sloqan
        slogan_label = QLabel("Səhiyyə Barmaqlarınızın Ucundadır!")
        slogan_font = QFont("Arial", 12)
        slogan_font.setItalic(True)
        slogan_label.setFont(slogan_font)
        slogan_label.setStyleSheet("color: #1976d2; margin: 0px;")
        
        text_layout.addWidget(title_label)
        text_layout.addWidget(slogan_label)
        title_layout.addWidget(text_widget)
        
        # Həkim məlumatları
        self.doctor_info_label = QLabel("Xoş gəlmisiniz")
        self.doctor_info_label.setFont(QFont("Arial", 12))
        self.doctor_info_label.setAlignment(Qt.AlignRight)
        
        # Çıxış düyməsi
        logout_btn = QPushButton("Çıxış")
        logout_btn.clicked.connect(self.logout)
        logout_btn.setMaximumWidth(100)
        
        header_layout.addWidget(title_widget)
        header_layout.addStretch()
        header_layout.addWidget(self.doctor_info_label)
        header_layout.addWidget(logout_btn)
        
        parent_layout.addWidget(header_frame)
    
    def create_tabs(self):
        """Tab pəncərələrini yaratma"""
        # Pasiyent Axtarışı
        self.patient_search_widget = PatientSearchWidget(self.db_manager)
        self.patient_search_widget.patient_selected.connect(self.on_patient_selected)
        self.tab_widget.addTab(self.patient_search_widget, "📋 Pasiyent Axtarışı")
        
        # Resept Yazma
        self.prescription_editor = PrescriptionEditorWidget(self.db_manager)
        self.tab_widget.addTab(self.prescription_editor, "📝 Resept Yazma")
        
        # Statistika
        self.statistics_dashboard = StatisticsDashboard(self.db_manager)
        self.tab_widget.addTab(self.statistics_dashboard, "📊 Statistika")
        
        # Tabların başlanğıc vəziyyəti
        self.tab_widget.setTabEnabled(1, False)  # Resept yazma - pasiyent seçiləndən sonra
        self.tab_widget.setTabEnabled(2, False)  # Statistika - həkim girişindən sonra
    
    def apply_style(self):
        """Aplikasiya stilini tətbiq etmə - BioScript mavi teması"""
        style = """
        QMainWindow {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                      stop:0 #f0f8ff, stop:1 #e1f5fe);
        }
        
        QFrame {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                      stop:0 #ffffff, stop:1 #f5f5f5);
            border: 1px solid #1e88e5;
            border-radius: 8px;
        }
        
        QTabWidget::pane {
            border: 2px solid #1e88e5;
            background-color: white;
            border-radius: 8px;
        }
        
        QTabBar::tab {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                      stop:0 #e3f2fd, stop:1 #bbdefb);
            padding: 12px 20px;
            margin-right: 3px;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            border: 1px solid #1e88e5;
            color: #1565c0;
            font-weight: bold;
        }
        
        QTabBar::tab:selected {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                      stop:0 #1e88e5, stop:1 #1976d2);
            color: white;
            border-bottom: none;
        }
        
        QTabBar::tab:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                      stop:0 #90caf9, stop:1 #64b5f6);
        }
        
        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                      stop:0 #1e88e5, stop:1 #1976d2);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            font-weight: bold;
            font-size: 14px;
        }
        
        QPushButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                      stop:0 #1976d2, stop:1 #1565c0);
        }
        
        QPushButton:pressed {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                      stop:0 #1565c0, stop:1 #0d47a1);
        }
        
        QLineEdit, QTextEdit, QComboBox {
            border: 2px solid #1e88e5;
            border-radius: 6px;
            padding: 8px 12px;
            font-size: 14px;
            background-color: white;
        }
        
        QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
            border-color: #1976d2;
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                      stop:0 #ffffff, stop:1 #f0f8ff);
        }
        
        QTableWidget {
            gridline-color: #1e88e5;
            selection-background-color: #bbdefb;
            border: 2px solid #1e88e5;
            border-radius: 6px;
            background-color: white;
        }
        
        QTableWidget::item {
            padding: 10px;
            border-bottom: 1px solid #e3f2fd;
        }
        
        QTableWidget::item:selected {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                      stop:0 #1e88e5, stop:1 #1976d2);
            color: white;
        }
        
        QTableWidget::horizontalHeader {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                      stop:0 #1e88e5, stop:1 #1976d2);
            color: white;
            font-weight: bold;
        }
        
        QGroupBox {
            font-weight: bold;
            border: 2px solid #1e88e5;
            border-radius: 8px;
            margin-top: 1ex;
            color: #1565c0;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
            background-color: white;
        }
        """
        
        self.setStyleSheet(style)
    
    def show_login(self):
        """Giriş pəncərəsini göstər"""
        login_window = DoctorLoginWindow(self.db_manager)
        login_window.login_successful.connect(self.on_login_successful)
        
        # Ana pəncərəni gizlət
        self.hide()
        
        # Giriş pəncərəsini göstər
        if login_window.exec_() == login_window.Rejected:
            # Giriş ləğv edilibsə, aplikasiyanı bağla
            sys.exit()
    
    def on_login_successful(self, doctor_data):
        """Uğurlu giriş"""
        self.current_doctor = doctor_data
        
        # Həkim məlumatlarını yenilə
        doctor_name = f"Dr. {doctor_data['name']} {doctor_data['surname']}"
        self.doctor_info_label.setText(f"Xoş gəlmisiniz, {doctor_name}")
        
        # Tabları aktivləşdir
        self.tab_widget.setTabEnabled(2, True)  # Statistika
        
        # Ana pəncərəni göstər
        self.show()
        
        # Statusu yenilə
        self.statusBar().showMessage(f"Giriş edildi: {doctor_name}")
        
        # Statistikaları yenilə
        if hasattr(self.statistics_dashboard, 'refresh_data'):
            self.statistics_dashboard.refresh_data(doctor_data['id'])
    
    def on_patient_selected(self, patient_data):
        """Pasiyent seçiləndə"""
        self.current_patient = patient_data
        
        # Resept yazma tabını aktivləşdir
        self.tab_widget.setTabEnabled(1, True)
        
        # Resept editoruna pasiyent məlumatlarını ötür
        self.prescription_editor.set_patient(patient_data)
        self.prescription_editor.set_doctor(self.current_doctor)
        
        # Resept yazma tabına keç
        self.tab_widget.setCurrentIndex(1)
        
        # Status
        patient_name = f"{patient_data['name']} {patient_data['surname']}"
        self.statusBar().showMessage(f"Pasiyent seçildi: {patient_name}")
    
    def logout(self):
        """Çıxış"""
        reply = QMessageBox.question(self, 'Çıxış', 
                                   'Sistemdən çıxmaq istədiyinizdən əminsiniz?',
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.current_doctor = None
            self.current_patient = None
            
            # Tabları deaktiv et
            self.tab_widget.setTabEnabled(1, False)
            self.tab_widget.setTabEnabled(2, False)
            self.tab_widget.setCurrentIndex(0)
            
            # Giriş pəncərəsini yenidən göstər
            self.show_login()
    
    def closeEvent(self, event):
        """Aplikasiya bağlananda"""
        reply = QMessageBox.question(self, 'Çıxış', 
                                   'Aplikasiyanı bağlamaq istədiyinizdən əminsiniz?',
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # Verilənlər bazası bağlantısını bağla
            if self.db_manager:
                self.db_manager.close_connection()
            event.accept()
        else:
            event.ignore()

def main():
    """Əsas funksiya"""
    app = QApplication(sys.argv)
    
    # Aplikasiya məlumatları
    app.setApplicationName("BioScript")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("BioScript Team")
    app.setApplicationDisplayName("BioScript - Səhiyyə Barmaqlarınızın Ucundadır!")
    
    # Ana pəncərə
    window = BioScriptMainWindow()
    
    # Çıxış işləyicisi
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()