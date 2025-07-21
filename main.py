#!/usr/bin/env python3
"""
BioScript - Tibbi Resept İdarəetmə Sistemi
Əsas aplikasiya faylı
"""

import sys
import os
from dotenv import load_dotenv
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                            QTabWidget, QTableWidget, QTableWidgetItem,
                            QTextEdit, QComboBox, QDateEdit, QMessageBox,
                            QSplitter, QFrame, QGridLayout, QScrollArea,
                            QGroupBox, QSpinBox, QFormLayout)
from PyQt5.QtCore import Qt, QDate, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QPalette, QColor, QPixmap

# .env faylını yüklə
load_dotenv()

from database.db_manager import DatabaseManager
from ui.new_doctor_login import NewDoctorLoginWindow
from ui.dashboard import BioScriptDashboard
from ui.new_streamlined_workflow import NewStreamlinedWorkflow
from gemini_ai import BioScriptAI

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
        
        # Mərkəzi widget stack
        self.central_stack = QTabWidget()
        self.central_stack.tabBar().setVisible(False)  # Tab bar gizlə
        self.setCentralWidget(self.central_stack)
        
        # Dashboard
        self.dashboard = None
        
        # Status bar
        self.statusBar().showMessage("Hazır")
    

    
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
        
        # Ana pəncərə arxa planı
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #f8f9fa, stop:1 #e9ecef);
            }
        """)
    
    def show_login(self):
        """Giriş pəncərəsini göstər"""
        login_window = NewDoctorLoginWindow(self.db_manager)
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
        
        # Dashboard yaratma
        self.dashboard = BioScriptDashboard(self.db_manager, doctor_data)
        self.dashboard.new_prescription_requested.connect(self.start_new_prescription)
        self.dashboard.view_prescriptions_requested.connect(self.view_prescriptions)
        
        # Dashboard-u stack-ə əlavə et
        self.central_stack.addWidget(self.dashboard)
        self.central_stack.setCurrentWidget(self.dashboard)
        
        # Ana pəncərəni göstər
        self.show()
        
        # Status yenilə
        doctor_name = f"Dr. {doctor_data['name']} {doctor_data['surname']}"
        self.statusBar().showMessage(f"Xoş gəlmisiniz, {doctor_name}")
    
    def start_new_prescription(self):
        """Yeni resept yazma prosesini başlatma - köhnə sistem"""
        # Bu artıq istifadə olunmur, yeni streamlined workflow dashboard-dan başlayır
        pass

        
    def on_prescription_saved(self, prescription_data):
        """Resept saxlanıldıqda"""
        QMessageBox.information(self, "Uğur", 
                              "Resept uğurla qeyd edildi!\n"
                              "Dashboard-a qayıdılır.")
        self.return_to_dashboard()
        
    def return_to_dashboard(self):
        """Dashboard-a qayıtma"""
        if self.dashboard:
            self.central_stack.setCurrentWidget(self.dashboard)
            
            # Analytics-i yenilə
            if hasattr(self.dashboard, 'analytics_widget'):
                self.dashboard.analytics_widget.load_analytics()
                
        doctor_name = f"Dr. {self.current_doctor['name']} {self.current_doctor['surname']}"
        self.statusBar().showMessage(f"Dashboard - {doctor_name}")
    
    def view_prescriptions(self):
        """Resept tarixçəsini göstərmə"""
        # Sadəlik üçün hal-hazırda mesaj göstərəcək
        # Gələcəkdə ayrı bir pəncərə ola bilər
        QMessageBox.information(self, "Məlumat", 
                              "Resept tarixçəsi funksiyası tezliklə əlavə ediləcək.")
    
    def logout(self):
        """Çıxış"""
        reply = QMessageBox.question(self, 'Çıxış', 
                                   'Sistemdən çıxmaq istədiyinizdən əminsiniz?',
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.current_doctor = None
            self.current_patient = None
            
            # Stack-i təmizlə
            while self.central_stack.count() > 0:
                widget = self.central_stack.widget(0)
                self.central_stack.removeWidget(widget)
                widget.deleteLater()
            
            self.dashboard = None
            
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