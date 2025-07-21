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
        self.setWindowTitle("BioScript - Tibbi Resept İdarəetmə Sistemi")
        self.setGeometry(100, 100, 1400, 900)
        
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
        title_label = QLabel("🏥 BioScript")
        title_label.setFont(QFont("Arial", 24, QFont.Bold))
        title_label.setStyleSheet("color: #2c3e50; padding: 10px;")
        
        # Həkim məlumatları
        self.doctor_info_label = QLabel("Xoş gəlmisiniz")
        self.doctor_info_label.setFont(QFont("Arial", 12))
        self.doctor_info_label.setAlignment(Qt.AlignRight)
        
        # Çıxış düyməsi
        logout_btn = QPushButton("Çıxış")
        logout_btn.clicked.connect(self.logout)
        logout_btn.setMaximumWidth(100)
        
        header_layout.addWidget(title_label)
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
        """Aplikasiya stilini tətbiq etmə"""
        style = """
        QMainWindow {
            background-color: #f8f9fa;
        }
        
        QTabWidget::pane {
            border: 1px solid #dee2e6;
            background-color: white;
        }
        
        QTabBar::tab {
            background-color: #e9ecef;
            padding: 8px 16px;
            margin-right: 2px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }
        
        QTabBar::tab:selected {
            background-color: white;
            border-bottom: 2px solid #007bff;
        }
        
        QPushButton {
            background-color: #007bff;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        }
        
        QPushButton:hover {
            background-color: #0056b3;
        }
        
        QPushButton:pressed {
            background-color: #004085;
        }
        
        QLineEdit, QTextEdit, QComboBox {
            border: 1px solid #ced4da;
            border-radius: 4px;
            padding: 8px;
            font-size: 14px;
        }
        
        QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
            border-color: #80bdff;
            outline: none;
        }
        
        QTableWidget {
            gridline-color: #dee2e6;
            selection-background-color: #e3f2fd;
        }
        
        QTableWidget::item {
            padding: 8px;
        }
        
        QTableWidget::item:selected {
            background-color: #1976d2;
            color: white;
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
    
    # Ana pəncərə
    window = BioScriptMainWindow()
    
    # Çıxış işləyicisi
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()