"""
BioScript - Resept Yazma Editoru
Resept yaratma və redaktə interfeysi
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
                            QTextEdit, QComboBox, QFormLayout, QGroupBox,
                            QSpinBox, QFrame, QSplitter, QScrollArea,
                            QMessageBox, QDateEdit, QHeaderView, QAbstractItemView)
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from PyQt5.QtGui import QFont

class PrescriptionEditorWidget(QWidget):
    """Resept yazma widget"""
    
    prescription_saved = pyqtSignal(int)  # prescription_id
    
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.current_patient = None
        self.current_doctor = None
        self.current_medications = []
        
        self.init_ui()
        self.load_medications_list()
    
    def init_ui(self):
        """İstifadəçi interfeysi başlatma"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        
        # Pasiyent məlumat başlığı
        self.create_patient_header(main_layout)
        
        # Splitter - resept formu və dərman siyahısı
        splitter = QSplitter(Qt.Horizontal)
        
        # Sol tərəf - resept formu
        self.create_prescription_form(splitter)
        
        # Sağ tərəf - dərman əlavə etmə
        self.create_medication_panel(splitter)
        
        # Splitter nisbətləri
        splitter.setStretchFactor(0, 2)  # Form
        splitter.setStretchFactor(1, 1)   # Dərmanlar
        
        main_layout.addWidget(splitter)
        
        # Alt hissə - əlavə edilmiş dərmanlar
        self.create_medications_table(main_layout)
        
        # Əməliyyat düymələri
        self.create_action_buttons(main_layout)
        
        # Başlanğıc vəziyyət
        self.set_enabled(False)
    
    def create_patient_header(self, parent_layout):
        """Pasiyent məlumat başlığı"""
        self.patient_header = QFrame()
        self.patient_header.setFrameStyle(QFrame.Box)
        self.patient_header.setStyleSheet("""
            QFrame {
                background-color: #e3f2fd;
                border: 2px solid #2196f3;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        
        header_layout = QHBoxLayout(self.patient_header)
        
        # Pasiyent məlumatları
        self.patient_info_label = QLabel("Pasiyent seçilməyib")
        self.patient_info_label.setFont(QFont("Arial", 14, QFont.Bold))
        self.patient_info_label.setStyleSheet("color: #1976d2;")
        
        # Tarix
        date_label = QLabel("Tarix:")
        self.prescription_date = QDateEdit()
        self.prescription_date.setDate(QDate.currentDate())
        self.prescription_date.setCalendarPopup(True)
        
        header_layout.addWidget(self.patient_info_label)
        header_layout.addStretch()
        header_layout.addWidget(date_label)
        header_layout.addWidget(self.prescription_date)
        
        parent_layout.addWidget(self.patient_header)
    
    def create_prescription_form(self, parent_widget):
        """Resept formu yaratma"""
        form_frame = QFrame()
        form_layout = QVBoxLayout(form_frame)
        
        # Şikayət
        complaint_group = QGroupBox("Pasiyent Şikayəti")
        complaint_layout = QVBoxLayout(complaint_group)
        
        self.complaint_text = QTextEdit()
        self.complaint_text.setPlaceholderText("Pasiyentin şikayətlərini qeyd edin...")
        self.complaint_text.setMaximumHeight(100)
        complaint_layout.addWidget(self.complaint_text)
        
        form_layout.addWidget(complaint_group)
        
        # Diaqnoz
        diagnosis_group = QGroupBox("Diaqnoz")
        diagnosis_layout = QVBoxLayout(diagnosis_group)
        
        self.diagnosis_text = QTextEdit()
        self.diagnosis_text.setPlaceholderText("Diaqnozu qeyd edin...")
        self.diagnosis_text.setMaximumHeight(100)
        diagnosis_layout.addWidget(self.diagnosis_text)
        
        form_layout.addWidget(diagnosis_group)
        
        # Qeydlər
        notes_group = QGroupBox("Əlavə Qeydlər")
        notes_layout = QVBoxLayout(notes_group)
        
        self.notes_text = QTextEdit()
        self.notes_text.setPlaceholderText("Əlavə qeydlər, tövsiyələr...")
        self.notes_text.setMaximumHeight(80)
        notes_layout.addWidget(self.notes_text)
        
        form_layout.addWidget(notes_group)
        form_layout.addStretch()
        
        parent_widget.addWidget(form_frame)
    
    def create_medication_panel(self, parent_widget):
        """Dərman əlavə etmə paneli"""
        med_frame = QFrame()
        med_layout = QVBoxLayout(med_frame)
        
        # Başlıq
        med_label = QLabel("Dərman Əlavə Et")
        med_label.setFont(QFont("Arial", 12, QFont.Bold))
        med_layout.addWidget(med_label)
        
        # Dərman formu
        med_form = QGroupBox("Dərman Məlumatları")
        form_layout = QFormLayout(med_form)
        
        # Dərman adı
        self.medication_combo = QComboBox()
        self.medication_combo.setEditable(True)
        self.medication_combo.setPlaceholderText("Dərman seçin və ya yazın...")
        form_layout.addRow("Dərman adı:", self.medication_combo)
        
        # Dozaj
        self.dosage_input = QLineEdit()
        self.dosage_input.setPlaceholderText("məs: 500mg")
        form_layout.addRow("Dozaj:", self.dosage_input)
        
        # Tezlik
        self.frequency_combo = QComboBox()
        self.frequency_combo.addItems([
            "Gündə 1 dəfə",
            "Gündə 2 dəfə", 
            "Gündə 3 dəfə",
            "Gündə 4 dəfə",
            "Hər 4 saatda bir",
            "Hər 6 saatda bir",
            "Hər 8 saatda bir",
            "Hər 12 saatda bir",
            "Lazım olduqda"
        ])
        self.frequency_combo.setEditable(True)
        form_layout.addRow("Tezlik:", self.frequency_combo)
        
        # Müddət
        self.duration_combo = QComboBox()
        self.duration_combo.addItems([
            "3 gün",
            "5 gün",
            "7 gün",
            "10 gün",
            "14 gün",
            "21 gün",
            "1 ay",
            "2 ay",
            "3 ay",
            "Həkimin tövsiyəsi ilə"
        ])
        self.duration_combo.setEditable(True)
        form_layout.addRow("Müddət:", self.duration_combo)
        
        # Miqdar
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setRange(1, 1000)
        self.quantity_spin.setValue(1)
        self.quantity_spin.setSuffix(" ədəd")
        form_layout.addRow("Miqdar:", self.quantity_spin)
        
        # İstifadə qaydaları
        self.instructions_text = QTextEdit()
        self.instructions_text.setPlaceholderText("İstifadə qaydalarını qeyd edin...")
        self.instructions_text.setMaximumHeight(60)
        form_layout.addRow("İstifadə qaydaları:", self.instructions_text)
        
        med_layout.addWidget(med_form)
        
        # Dərman əlavə et düyməsi
        add_med_btn = QPushButton("➕ Dərman Əlavə Et")
        add_med_btn.clicked.connect(self.add_medication)
        add_med_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                font-weight: bold;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        med_layout.addWidget(add_med_btn)
        med_layout.addStretch()
        
        parent_widget.addWidget(med_frame)
    
    def create_medications_table(self, parent_layout):
        """Əlavə edilmiş dərmanlar cədvəli"""
        table_group = QGroupBox("Təyin Edilmiş Dərmanlar")
        table_layout = QVBoxLayout(table_group)
        
        # Cədvəl
        self.medications_table = QTableWidget()
        self.medications_table.setColumnCount(6)
        self.medications_table.setHorizontalHeaderLabels([
            "Dərman Adı", "Dozaj", "Tezlik", "Müddət", "Miqdar", "Qeydlər"
        ])
        
        # Cədvəl parametrləri
        self.medications_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.medications_table.setAlternatingRowColors(True)
        self.medications_table.setMaximumHeight(200)
        
        # Sütun genişlikləri
        header = self.medications_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Dərman adı
        
        table_layout.addWidget(self.medications_table)
        
        # Cədvəl düymələri
        table_buttons = QHBoxLayout()
        
        # Dərmanı sil
        self.remove_med_btn = QPushButton("🗑️ Seçilmiş Dərmanı Sil")
        self.remove_med_btn.clicked.connect(self.remove_medication)
        self.remove_med_btn.setEnabled(False)
        
        # Cədvəli təmizlə
        clear_table_btn = QPushButton("🧹 Hamısını Təmizlə")
        clear_table_btn.clicked.connect(self.clear_medications)
        
        table_buttons.addWidget(self.remove_med_btn)
        table_buttons.addWidget(clear_table_btn)
        table_buttons.addStretch()
        
        table_layout.addLayout(table_buttons)
        
        # Cədvəl seçim hadisəsi
        self.medications_table.itemSelectionChanged.connect(self.on_medication_selection_changed)
        
        parent_layout.addWidget(table_group)
    
    def create_action_buttons(self, parent_layout):
        """Əməliyyat düymələri"""
        button_layout = QHBoxLayout()
        
        # Resepti yadda saxla
        self.save_btn = QPushButton("💾 Resepti Yadda Saxla")
        self.save_btn.clicked.connect(self.save_prescription)
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                font-weight: bold;
                padding: 12px 24px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        
        # Formu təmizlə
        clear_btn = QPushButton("🧹 Formu Təmizlə")
        clear_btn.clicked.connect(self.clear_form)
        
        # Pasiyent tarixçəsi
        self.history_btn = QPushButton("📜 Pasiyent Tarixçəsi")
        self.history_btn.clicked.connect(self.show_patient_history)
        
        button_layout.addWidget(clear_btn)
        button_layout.addWidget(self.history_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.save_btn)
        
        parent_layout.addLayout(button_layout)
    
    def load_medications_list(self):
        """Dərmanlar siyahısını yükləmə"""
        try:
            medications = self.db_manager.get_medications_list()
            self.medication_combo.clear()
            
            for med in medications:
                # Dərman adı və kateqoriya
                display_text = f"{med['name']} ({med.get('category', 'Ümumi')})"
                self.medication_combo.addItem(display_text, med)
                
        except Exception as e:
            print(f"Dərmanlar yükləmə xətası: {e}")
    
    def set_patient(self, patient_data):
        """Pasiyent məlumatlarını təyin etmə"""
        self.current_patient = patient_data
        
        # Header məlumatını yenilə
        patient_name = f"{patient_data['name']} {patient_data['surname']}"
        patient_info = f"👤 {patient_name} • ID: {patient_data['id']}"
        if patient_data.get('birth_date'):
            patient_info += f" • Doğum: {patient_data['birth_date']}"
        
        self.patient_info_label.setText(patient_info)
        
        # Formu aktiv et
        self.set_enabled(True)
    
    def set_doctor(self, doctor_data):
        """Həkim məlumatlarını təyin etmə"""
        self.current_doctor = doctor_data
    
    def set_enabled(self, enabled):
        """Widget elementlərini aktiv/deaktiv etmə"""
        self.complaint_text.setEnabled(enabled)
        self.diagnosis_text.setEnabled(enabled)
        self.notes_text.setEnabled(enabled)
        self.medication_combo.setEnabled(enabled)
        self.dosage_input.setEnabled(enabled)
        self.frequency_combo.setEnabled(enabled)
        self.duration_combo.setEnabled(enabled)
        self.quantity_spin.setEnabled(enabled)
        self.instructions_text.setEnabled(enabled)
        self.save_btn.setEnabled(enabled)
        self.history_btn.setEnabled(enabled)
    
    def add_medication(self):
        """Dərman əlavə etmə"""
        # Validasiya
        medication_name = self.medication_combo.currentText().strip()
        dosage = self.dosage_input.text().strip()
        frequency = self.frequency_combo.currentText().strip()
        duration = self.duration_combo.currentText().strip()
        
        if not medication_name:
            QMessageBox.warning(self, "Xəta", "Dərman adını daxil edin!")
            return
        
        if not dosage:
            QMessageBox.warning(self, "Xəta", "Dozajı daxil edin!")
            return
        
        # Dərman obyekti
        medication = {
            'medication_name': medication_name,
            'dosage': dosage,
            'frequency': frequency,
            'duration': duration,
            'quantity': self.quantity_spin.value(),
            'instructions': self.instructions_text.toPlainText().strip()
        }
        
        # Siyahıya əlavə et
        self.current_medications.append(medication)
        
        # Cədvəli yenilə
        self.update_medications_table()
        
        # Formu təmizlə
        self.clear_medication_form()
    
    def update_medications_table(self):
        """Dərmanlar cədvəlini yeniləmə"""
        self.medications_table.setRowCount(len(self.current_medications))
        
        for row, med in enumerate(self.current_medications):
            self.medications_table.setItem(row, 0, QTableWidgetItem(med['medication_name']))
            self.medications_table.setItem(row, 1, QTableWidgetItem(med['dosage']))
            self.medications_table.setItem(row, 2, QTableWidgetItem(med['frequency']))
            self.medications_table.setItem(row, 3, QTableWidgetItem(med['duration']))
            self.medications_table.setItem(row, 4, QTableWidgetItem(str(med['quantity'])))
            self.medications_table.setItem(row, 5, QTableWidgetItem(med['instructions']))
        
        # Sütun genişliklərini yenilə
        self.medications_table.resizeColumnsToContents()
    
    def clear_medication_form(self):
        """Dərman formu təmizləmə"""
        self.medication_combo.setCurrentIndex(-1)
        self.dosage_input.clear()
        self.frequency_combo.setCurrentIndex(0)
        self.duration_combo.setCurrentIndex(0)
        self.quantity_spin.setValue(1)
        self.instructions_text.clear()
    
    def remove_medication(self):
        """Seçilmiş dərmanı silmə"""
        selected_rows = self.medications_table.selectionModel().selectedRows()
        
        if not selected_rows:
            return
        
        row = selected_rows[0].row()
        
        # Təsdiq
        reply = QMessageBox.question(self, 'Təsdiq', 
                                   'Seçilmiş dərmanı silmək istədiyinizdən əminsiniz?',
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # Siyahıdan sil
            del self.current_medications[row]
            
            # Cədvəli yenilə
            self.update_medications_table()
    
    def clear_medications(self):
        """Bütün dərmanları təmizləmə"""
        if not self.current_medications:
            return
        
        reply = QMessageBox.question(self, 'Təsdiq', 
                                   'Bütün dərmanları silmək istədiyinizdən əminsiniz?',
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.current_medications.clear()
            self.update_medications_table()
    
    def on_medication_selection_changed(self):
        """Dərman seçimi dəyişəndə"""
        selected = len(self.medications_table.selectionModel().selectedRows()) > 0
        self.remove_med_btn.setEnabled(selected)
    
    def save_prescription(self):
        """Resepti yadda saxlama"""
        if not self.current_patient or not self.current_doctor:
            QMessageBox.warning(self, "Xəta", "Pasiyent və ya həkim məlumatı yoxdur!")
            return
        
        if not self.current_medications:
            QMessageBox.warning(self, "Xəta", "Ən azı bir dərman əlavə edin!")
            return
        
        # Resept məlumatları
        prescription_data = {
            'doctor_id': self.current_doctor['id'],
            'patient_id': self.current_patient['id'],
            'complaint': self.complaint_text.toPlainText().strip(),
            'diagnosis': self.diagnosis_text.toPlainText().strip(),
            'notes': self.notes_text.toPlainText().strip(),
            'medications': self.current_medications
        }
        
        try:
            # Verilənlər bazasında saxla
            prescription_id = self.db_manager.create_prescription(prescription_data)
            
            if prescription_id:
                QMessageBox.information(self, "Uğur", 
                                      f"Resept uğurla yaradıldı!\nResept ID: {prescription_id}")
                
                # Siqnal göndər
                self.prescription_saved.emit(prescription_id)
                
                # Formu təmizlə
                self.clear_form()
            else:
                QMessageBox.critical(self, "Xəta", "Resept yaradılmadı!")
                
        except Exception as e:
            QMessageBox.critical(self, "Xəta", f"Resept saxlama xətası: {str(e)}")
    
    def clear_form(self):
        """Formu təmizləmə"""
        self.complaint_text.clear()
        self.diagnosis_text.clear()
        self.notes_text.clear()
        self.current_medications.clear()
        self.update_medications_table()
        self.clear_medication_form()
        self.prescription_date.setDate(QDate.currentDate())
    
    def show_patient_history(self):
        """Pasiyent tarixçəsini göstərmə"""
        if not self.current_patient:
            return
        
        QMessageBox.information(self, "Məlumat", 
                               "Pasiyent tarixçəsi funksiyası hazırlanır...")