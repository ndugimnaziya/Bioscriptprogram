#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                            QListWidget, QListWidgetItem, QWidget, QCheckBox,
                            QLineEdit, QMessageBox, QScrollArea, QFrame)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QBrush, QLinearGradient, QColor
from datetime import datetime

class SalesDialog(QDialog):
    def __init__(self, user_data, db, parent=None):
        super().__init__(parent)
        self.user_data = user_data
        self.db = db
        self.selected_prescription = None
        self.medication_items = []
        self.total_price = 0.0
        self.init_ui()
        self.load_active_prescriptions()
        
    def init_ui(self):
        """Satış dialoqu UI-ni hazırla"""
        self.setWindowTitle("BioScript - Yeni Satış")
        self.setFixedSize(1000, 700)
        self.setWindowFlags(Qt.Dialog)
        
        # Mərkəzləşdirmək
        if self.parent():
            parent_pos = self.parent().pos()
            parent_size = self.parent().size()
            x = parent_pos.x() + (parent_size.width() - 1000) // 2
            y = parent_pos.y() + (parent_size.height() - 700) // 2
            self.move(x, y)
        
        # Ana layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Başlıq
        title_label = QLabel("💊 Aktiv Reseptlər - Satış üçün seçin")
        title_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title_label.setStyleSheet("color: #00BCD4; padding: 10px;")
        title_label.setAlignment(Qt.AlignCenter)
        
        # Resept siyahısı
        self.prescriptions_list = QListWidget()
        self.prescriptions_list.setStyleSheet("""
            QListWidget {
                border: 2px solid #E0E0E0;
                border-radius: 10px;
                background: white;
                font-size: 12pt;
            }
            QListWidget::item {
                padding: 15px;
                border-bottom: 1px solid #EEEEEE;
                background: white;
            }
            QListWidget::item:selected {
                background: #E3F2FD;
                color: #1976D2;
            }
            QListWidget::item:hover {
                background: #F5F5F5;
            }
        """)
        self.prescriptions_list.itemClicked.connect(self.on_prescription_selected)
        
        # Dərman siyahısı bölməsi (başlanğıcda gizli)
        self.medications_frame = QFrame()
        self.medications_frame.setVisible(False)
        self.medications_frame.setStyleSheet("""
            QFrame {
                border: 2px solid #4CAF50;
                border-radius: 10px;
                background: #F8FFF8;
                padding: 15px;
            }
        """)
        
        medications_layout = QVBoxLayout(self.medications_frame)
        
        meds_title = QLabel("🏥 Resept Dərmanları - Mövcud olanları ✓ edin")
        meds_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        meds_title.setStyleSheet("color: #4CAF50; margin-bottom: 10px;")
        
        # Scroll area dərmanlar üçün
        scroll_area = QScrollArea()
        scroll_area.setFixedHeight(200)
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #CCCCCC;
                border-radius: 5px;
                background: white;
            }
        """)
        
        self.medications_widget = QWidget()
        self.medications_layout = QVBoxLayout(self.medications_widget)
        scroll_area.setWidget(self.medications_widget)
        
        medications_layout.addWidget(meds_title)
        medications_layout.addWidget(scroll_area)
        
        # Yekun qiymət və satış düyməsi
        self.total_frame = QFrame()
        self.total_frame.setVisible(False)
        self.total_frame.setStyleSheet("""
            QFrame {
                background: #E8F5E8;
                border: 2px solid #4CAF50;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        
        total_layout = QHBoxLayout(self.total_frame)
        
        self.total_label = QLabel("Yekun: 0.00 ₼")
        self.total_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        self.total_label.setStyleSheet("color: #2E7D32;")
        
        sell_button = QPushButton("💰 SATIŞI TƏSDİQLƏ")
        sell_button.setFixedSize(200, 50)
        sell_button.setFont(QFont("Segoe UI", 12, QFont.Bold))
        sell_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4CAF50, stop:1 #388E3C);
                color: white;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #66BB6A, stop:1 #4CAF50);
            }
        """)
        sell_button.clicked.connect(self.complete_sale)
        
        total_layout.addWidget(self.total_label)
        total_layout.addStretch()
        total_layout.addWidget(sell_button)
        
        # Bağla düyməsi
        close_button = QPushButton("❌ Bağla")
        close_button.setFixedSize(100, 35)
        close_button.setStyleSheet("""
            QPushButton {
                background: #F44336;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover { background: #D32F2F; }
        """)
        close_button.clicked.connect(self.reject)
        
        # Layout-a əlavə et
        main_layout.addWidget(title_label)
        main_layout.addWidget(self.prescriptions_list, 1)
        main_layout.addWidget(self.medications_frame)
        main_layout.addWidget(self.total_frame)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        main_layout.addLayout(button_layout)
        
    def load_active_prescriptions(self):
        """Aktiv reseptləri yüklə"""
        if not self.db.connect():
            QMessageBox.critical(self, "Xəta", "Verilənlər bazasına qoşula bilmədi!")
            return
            
        query = """
            SELECT p.*, pat.name as patient_name, d.name as doctor_name, h.name as hospital_name
            FROM prescriptions p
            JOIN patients pat ON p.patient_id = pat.id  
            JOIN doctors d ON p.doctor_id = d.id
            JOIN hospitals h ON p.hospital_id = h.id
            WHERE p.status = 'active'
            ORDER BY p.issued_at DESC
        """
        
        prescriptions = self.db.execute_query(query)
        
        self.prescriptions_list.clear()
        
        if prescriptions:
            for prescription in prescriptions:
                item_text = f"📋 Resept #{prescription['id']} - {prescription['patient_name']}\n"
                item_text += f"   👨‍⚕️ Dr. {prescription['doctor_name']} ({prescription['hospital_name']})\n"
                item_text += f"   📅 {prescription['issued_at'].strftime('%d.%m.%Y %H:%M')}"
                
                if prescription['diagnosis']:
                    item_text += f"\n   🩺 Diaqnoz: {prescription['diagnosis']}"
                
                item = QListWidgetItem(item_text)
                item.setData(Qt.UserRole, prescription)
                self.prescriptions_list.addItem(item)
        else:
            item = QListWidgetItem("Aktiv resept tapılmadı")
            item.setFlags(item.flags() & ~Qt.ItemIsSelectable)
            self.prescriptions_list.addItem(item)
            
        self.db.disconnect()
        
    def on_prescription_selected(self, item):
        """Resept seçildikdə"""
        prescription_data = item.data(Qt.UserRole)
        if not prescription_data:
            return
            
        self.selected_prescription = prescription_data
        self.load_prescription_medications(prescription_data['id'])
        
    def load_prescription_medications(self, prescription_id):
        """Reseptin dərmanlarını yüklə"""
        if not self.db.connect():
            return
            
        query = """
            SELECT * FROM prescription_items 
            WHERE prescription_id = %s
        """
        
        medications = self.db.execute_query(query, (prescription_id,))
        
        # Köhnə dərmanları təmizlə
        for i in reversed(range(self.medications_layout.count())):
            self.medications_layout.itemAt(i).widget().setParent(None)
            
        self.medication_items = []
        
        if medications:
            for med in medications:
                med_item = MedicationItem(med, self)
                med_item.price_changed.connect(self.update_total)
                self.medications_layout.addWidget(med_item)
                self.medication_items.append(med_item)
                
        self.medications_frame.setVisible(True)
        self.total_frame.setVisible(True)
        self.update_total()
        
        self.db.disconnect()
        
    def update_total(self):
        """Yekun qiyməti yenilə"""
        self.total_price = 0.0
        for item in self.medication_items:
            if item.is_available_checkbox.isChecked() and item.price_input.text():
                try:
                    price = float(item.price_input.text())
                    self.total_price = float(self.total_price) + price
                except ValueError:
                    pass
                    
        self.total_label.setText(f"Yekun: {self.total_price:.2f} ₼")
        
    def complete_sale(self):
        """Satışı tamamla"""
        if not self.selected_prescription:
            QMessageBox.warning(self, "Xəta", "Resept seçilməyib!")
            return
            
        # Heç olmasa bir dərman seçilməlidiir
        selected_meds = [item for item in self.medication_items 
                        if item.is_available_checkbox.isChecked()]
        
        if not selected_meds:
            QMessageBox.warning(self, "Xəta", "Heç olmasa bir dərman seçin!")
            return
            
        # Qiymətlər boş olmamalıdır
        for item in selected_meds:
            if not item.price_input.text().strip():
                QMessageBox.warning(self, "Xəta", "Bütün seçilmiş dərmanların qiymətini daxil edin!")
                return
                
        if self.total_price <= 0:
            QMessageBox.warning(self, "Xəta", "Yekun qiymət sıfırdan böyük olmalıdır!")
            return
            
        # Satışı bazaya yaz
        if self.save_sale():
            QMessageBox.information(self, "Uğur", f"Satış uğurla tamamlandı!\nYekun: {self.total_price:.2f} ₼")
            self.accept()
        else:
            QMessageBox.critical(self, "Xəta", "Satış yadda saxlanarkən xəta yarandı!")
            
    def save_sale(self):
        """Satışı verilənlər bazasına yaz"""
        if not self.db.connect():
            return False
            
        try:
            # Komisyon məbləği hesabla (3%)
            commission_rate = float(self.user_data.get('commission_rate', 3.0))
            commission = float(self.total_price) * (commission_rate / 100.0)
            
            # dispensing_logs cədvəlinə əlavə et
            insert_query = """
                INSERT INTO dispensing_logs 
                (prescription_id, pharmacy_id, staff_id, patient_id, total_price, commission_amount)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            
            self.db.execute_insert(insert_query, (
                self.selected_prescription['id'],
                self.user_data['pharmacy_id'],
                self.user_data['id'],
                self.selected_prescription['patient_id'],
                float(self.total_price),
                float(commission)
            ))
            
            # Reseptin statusunu yenilə
            status_query = """
                UPDATE prescriptions 
                SET status = 'partially_dispensed'
                WHERE id = %s
            """
            self.db.execute_query(status_query, (self.selected_prescription['id'],))
            
            # Aptekin komisyon məbləğini yenilə  
            commission_query = """
                UPDATE pharmacies 
                SET current_month_commission = current_month_commission + %s
                WHERE id = %s
            """
            self.db.execute_query(commission_query, (float(commission), self.user_data['pharmacy_id']))
            
            return True
            
        except Exception as e:
            print(f"Satış saxlanarkən xəta: {e}")
            return False
        finally:
            self.db.disconnect()


class MedicationItem(QWidget):
    price_changed = pyqtSignal()
    
    def __init__(self, medication_data, parent=None):
        super().__init__(parent)
        self.medication_data = medication_data
        self.init_ui()
        
    def init_ui(self):
        """Dərman elementi UI-ni hazırla"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # Checkbox - aptekdə var/yoxdur
        self.is_available_checkbox = QCheckBox()
        self.is_available_checkbox.setFixedSize(20, 20)
        self.is_available_checkbox.stateChanged.connect(self.on_availability_changed)
        
        # Dərman adı və məlumatları
        info_text = f"💊 {self.medication_data['name']}"
        if self.medication_data['dosage']:
            info_text += f" ({self.medication_data['dosage']})"
        if self.medication_data['instructions']:
            info_text += f"\n   📝 {self.medication_data['instructions']}"
            
        info_label = QLabel(info_text)
        info_label.setFont(QFont("Segoe UI", 10))
        info_label.setStyleSheet("color: #333; padding: 5px;")
        info_label.setWordWrap(True)
        
        # Qiymət sahəsi
        price_label = QLabel("Qiymət:")
        price_label.setFont(QFont("Segoe UI", 10))
        price_label.setStyleSheet("color: #666;")
        
        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText("0.00")
        self.price_input.setFixedSize(80, 25)
        self.price_input.setEnabled(False)
        self.price_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #CCCCCC;
                border-radius: 4px;
                padding: 2px 5px;
            }
            QLineEdit:enabled {
                background: white;
                border-color: #4CAF50;
            }
            QLineEdit:disabled {
                background: #F5F5F5;
            }
        """)
        self.price_input.textChanged.connect(self.price_changed.emit)
        
        currency_label = QLabel("₼")
        currency_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        currency_label.setStyleSheet("color: #4CAF50;")
        
        # Layout düzəni
        layout.addWidget(self.is_available_checkbox)
        layout.addWidget(info_label, 1)
        layout.addWidget(price_label)
        layout.addWidget(self.price_input)
        layout.addWidget(currency_label)
        
    def on_availability_changed(self, state):
        """Mövcudluq vəziyyəti dəyişdikdə"""
        is_available = state == Qt.Checked
        self.price_input.setEnabled(is_available)
        
        if not is_available:
            self.price_input.clear()
            
        self.price_changed.emit()