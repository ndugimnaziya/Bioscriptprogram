#!/usr/bin/env python3
"""
BioScript - Pasiyent Tarixçəsi və AI Köməkçisi
Keçmiş reseptlərin AI ilə təhlili və yeni resept yazma
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QFrame, QListWidget, QListWidgetItem,
                            QTextEdit, QLineEdit, QFormLayout, QDateEdit,
                            QComboBox, QMessageBox, QGroupBox, QScrollArea,
                            QSplitter, QTabWidget, QTableWidget, QTableWidgetItem,
                            QSpinBox, QPlainTextEdit)
from PyQt5.QtCore import Qt, pyqtSignal, QDate, QThread, QTimer
from PyQt5.QtGui import QFont
from datetime import datetime, date
import json

from gemini_ai import BioScriptAI

class PatientHistoryAIWidget(QWidget):
    """Pasiyent tarixçəsi və AI köməkçili resept yazma"""
    
    prescription_completed = pyqtSignal()  # Resept tamamlandı
    
    def __init__(self, db_manager, patient_data, doctor_id):
        super().__init__()
        self.db_manager = db_manager
        self.patient_data = patient_data
        self.doctor_id = doctor_id
        self.ai_assistant = BioScriptAI()
        self.patient_history = []
        
        self.init_ui()
        self.load_patient_history()
        
    def init_ui(self):
        """UI yaratma"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Pasiyent məlumatları başlığı
        patient_info = QLabel(f"👤 {self.patient_data['ad']} {self.patient_data['soyad']} - Yaş: {self.patient_data['yaş']}")
        patient_info.setFont(QFont("Segoe UI", 18, QFont.Bold))
        patient_info.setAlignment(Qt.AlignCenter)
        patient_info.setStyleSheet("""
            color: #1565c0; 
            margin-bottom: 15px;
            padding: 15px;
            background: #e3f2fd;
            border-radius: 15px;
        """)
        layout.addWidget(patient_info)
        
        # Ana splitter
        main_splitter = QSplitter(Qt.Horizontal)
        
        # Sol tərəf - Keçmiş reseptlər
        history_frame = QGroupBox("📋 Keçmiş Reseptlər")
        history_frame.setFont(QFont("Segoe UI", 14, QFont.Bold))
        history_frame.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e3f2fd;
                border-radius: 10px;
                margin: 10px;
                padding: 15px;
                background: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px;
                color: #1565c0;
                background: white;
            }
        """)
        
        history_layout = QVBoxLayout(history_frame)
        
        # Keçmiş reseptlər listi
        self.history_list = QListWidget()
        self.history_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                background: #fafafa;
                padding: 8px;
                font-family: 'Segoe UI';
                font-size: 12px;
            }
            QListWidget::item {
                padding: 12px;
                border-bottom: 1px solid #e0e0e0;
                border-radius: 4px;
                margin: 2px 0;
                background: white;
            }
            QListWidget::item:hover {
                background: #f0f8ff;
            }
            QListWidget::item:selected {
                background: #e3f2fd;
                color: #1565c0;
            }
        """)
        
        history_layout.addWidget(self.history_list)
        
        # AI təhlil düyməsi
        self.ai_analyze_btn = QPushButton("🤖 AI Təhlil Et")
        self.ai_analyze_btn.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.ai_analyze_btn.setFixedHeight(40)
        self.ai_analyze_btn.clicked.connect(self.analyze_with_ai)
        self.ai_analyze_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #ff9800, stop:1 #f57c00);
                color: white;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #ffb74d, stop:1 #ff9800);
            }
        """)
        history_layout.addWidget(self.ai_analyze_btn)
        
        main_splitter.addWidget(history_frame)
        
        # Sağ tərəf - Yeni resept yazma
        prescription_frame = QGroupBox("📝 Yeni Resept")
        prescription_frame.setFont(QFont("Segoe UI", 14, QFont.Bold))
        prescription_frame.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e3f2fd;
                border-radius: 10px;
                margin: 10px;
                padding: 15px;
                background: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px;
                color: #1565c0;
                background: white;
            }
        """)
        
        prescription_layout = QVBoxLayout(prescription_frame)
        
        # AI tövsiyələri sahəsi
        self.ai_recommendations = QTextEdit()
        self.ai_recommendations.setPlaceholderText("AI təhlil edildikdən sonra tövsiyələr burada görünəcək...")
        self.ai_recommendations.setMaximumHeight(150)
        self.ai_recommendations.setStyleSheet("""
            QTextEdit {
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                padding: 10px;
                background: #f8f9fa;
                font-family: 'Segoe UI';
                font-size: 12px;
            }
        """)
        self.ai_recommendations.setReadOnly(True)
        prescription_layout.addWidget(QLabel("🤖 AI Tövsiyələri:"))
        prescription_layout.addWidget(self.ai_recommendations)
        
        # Resept formu
        form_scroll = QScrollArea()
        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        form_layout.setSpacing(15)
        
        # Şikayət
        self.complaint_input = QPlainTextEdit()
        self.complaint_input.setPlaceholderText("Pasiyentin hal-hazırkı şikayətlərini daxil edin...")
        self.complaint_input.setMaximumHeight(80)
        
        # Diaqnoz
        self.diagnosis_input = QLineEdit()
        self.diagnosis_input.setPlaceholderText("Qoyulan diaqnozu daxil edin...")
        
        # Dərmanlar cədvəli
        self.medications_table = QTableWidget(0, 4)
        self.medications_table.setHorizontalHeaderLabels(["Dərman Adı", "Dozaj", "İstifadə Qaydası", "Müddət"])
        self.medications_table.setMaximumHeight(200)
        
        # Input stilləri
        input_style = """
            QLineEdit, QPlainTextEdit, QTableWidget {
                padding: 8px;
                border: 2px solid #e0e0e0;
                border-radius: 6px;
                font-size: 14px;
                background: white;
            }
            QLineEdit:focus, QPlainTextEdit:focus {
                border-color: #1e88e5;
            }
        """
        
        for widget in [self.complaint_input, self.diagnosis_input, self.medications_table]:
            widget.setStyleSheet(input_style)
        
        # Form əlavə et
        form_layout.addRow("🩺 Şikayət:", self.complaint_input)
        form_layout.addRow("🔬 Diaqnoz:", self.diagnosis_input)
        form_layout.addRow("💊 Dərmanlar:", self.medications_table)
        
        # Dərman əlavə düyməsi
        add_med_btn = QPushButton("➕ Dərman Əlavə Et")
        add_med_btn.clicked.connect(self.add_medication_row)
        add_med_btn.setStyleSheet("""
            QPushButton {
                background: #4caf50;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 6px;
                font-weight: bold;
            }
        """)
        form_layout.addRow("", add_med_btn)
        
        form_scroll.setWidget(form_widget)
        form_scroll.setWidgetResizable(True)
        prescription_layout.addWidget(form_scroll)
        
        # Resept yadda saxla düyməsi
        self.save_prescription_btn = QPushButton("💾 Resepti Yadda Saxla")
        self.save_prescription_btn.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.save_prescription_btn.setFixedHeight(50)
        self.save_prescription_btn.clicked.connect(self.save_prescription)
        self.save_prescription_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #1e88e5, stop:1 #1976d2);
                color: white;
                border: none;
                border-radius: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #42a5f5, stop:1 #1e88e5);
            }
        """)
        prescription_layout.addWidget(self.save_prescription_btn)
        
        main_splitter.addWidget(prescription_frame)
        
        # Splitter nisbətləri
        main_splitter.setSizes([400, 600])
        
        layout.addWidget(main_splitter)
        
    def load_patient_history(self):
        """Pasiyent tarixçəsini yüklə"""
        try:
            connection = self.db_manager.get_connection()
            cursor = connection.cursor()
            
            query = """
            SELECT r.id, r.şikayət, r.diaqnoz, r.dərmanlar, r.yaradılma_tarixi,
                   h.ad as hekim_adi, h.soyad as hekim_soyadi
            FROM reseptlər r
            JOIN həkimlər h ON r.həkim_id = h.id
            WHERE r.pasiyent_id = %s
            ORDER BY r.yaradılma_tarixi DESC
            LIMIT 10
            """
            
            cursor.execute(query, (self.patient_data['id'],))
            prescriptions = cursor.fetchall()
            
            self.patient_history = []
            self.history_list.clear()
            
            for prescription in prescriptions:
                presc_id, sikayət, diaqnoz, dərmanlar, yaradilma, hekim_ad, hekim_soyad = prescription
                
                # Dərmanları parse et
                try:
                    if dərmanlar:
                        meds = json.loads(dərmanlar) if isinstance(dərmanlar, str) else dərmanlar
                    else:
                        meds = []
                except:
                    meds = []
                
                # Tarixçə məlumatlarını saxla
                history_item = {
                    'id': presc_id,
                    'şikayət': sikayət,
                    'diaqnoz': diaqnoz,
                    'dərmanlar': meds,
                    'tarix': yaradilma,
                    'həkim': f"{hekim_ad} {hekim_soyad}"
                }
                self.patient_history.append(history_item)
                
                # List widget-ə əlavə et
                item_text = f"""
                📅 {yaradilma.strftime('%d.%m.%Y')} - Dr. {hekim_ad} {hekim_soyad}
                🩺 Şikayət: {sikayət[:50]}{'...' if len(sikayət) > 50 else ''}
                🔬 Diaqnoz: {diaqnoz[:50]}{'...' if len(diaqnoz) > 50 else ''}
                💊 Dərman sayı: {len(meds)}
                """
                
                item = QListWidgetItem(item_text.strip())
                item.setData(Qt.UserRole, history_item)
                self.history_list.addItem(item)
                
            cursor.close()
            connection.close()
            
        except Exception as e:
            QMessageBox.warning(self, "Xəta", f"Pasiyent tarixçəsi yüklənərkən xəta: {str(e)}")
            
    def analyze_with_ai(self):
        """AI ilə pasiyent tarixçəsini təhlil et"""
        if not self.patient_history:
            QMessageBox.information(self, "Məlumat", "Bu pasiyentin keçmiş resepti yoxdur.")
            return
            
        self.ai_analyze_btn.setEnabled(False)
        self.ai_analyze_btn.setText("🤖 Təhlil edilir...")
        
        # AI üçün tarixçə məlumatlarını hazırla
        history_text = self.prepare_history_for_ai()
        
        # AI təhlil thread-də işə sal
        self.ai_thread = AIAnalysisThread(self.ai_assistant, self.patient_data, history_text)
        self.ai_thread.analysis_completed.connect(self.on_ai_analysis_completed)
        self.ai_thread.start()
        
    def prepare_history_for_ai(self):
        """AI üçün tarixçə mətnini hazırla"""
        history_text = f"Pasiyent: {self.patient_data['ad']} {self.patient_data['soyad']}, Yaş: {self.patient_data['yaş']}\n\n"
        history_text += "KEÇMİŞ RESEPTLƏRİ:\n"
        
        for i, item in enumerate(self.patient_history, 1):
            history_text += f"\n{i}. Resept ({item['tarix'].strftime('%d.%m.%Y')}):\n"
            history_text += f"   Şikayət: {item['şikayət']}\n"
            history_text += f"   Diaqnoz: {item['diaqnoz']}\n"
            history_text += f"   Dərmanlar:\n"
            
            for med in item['dərmanlar']:
                if isinstance(med, dict):
                    history_text += f"     - {med.get('ad', 'Bilinməyən')}: {med.get('dozaj', '')} {med.get('qaydalar', '')}\n"
                else:
                    history_text += f"     - {med}\n"
                    
        return history_text
        
    def on_ai_analysis_completed(self, analysis_result):
        """AI təhlil tamamlandı"""
        self.ai_analyze_btn.setEnabled(True)
        self.ai_analyze_btn.setText("🤖 AI Təhlil Et")
        
        if analysis_result:
            self.ai_recommendations.setPlainText(analysis_result)
        else:
            self.ai_recommendations.setPlainText("AI təhlil zamanı xəta baş verdi.")
            
    def add_medication_row(self):
        """Dərman cədvəlinə yeni sətir əlavə et"""
        row_count = self.medications_table.rowCount()
        self.medications_table.insertRow(row_count)
        
        # Hər sütun üçün boş item əlavə et
        for col in range(4):
            item = QTableWidgetItem("")
            self.medications_table.setItem(row_count, col, item)
            
    def save_prescription(self):
        """Resepti yadda saxla"""
        # Məcburi sahələri yoxla
        if not self.complaint_input.toPlainText().strip():
            QMessageBox.warning(self, "Xəta", "Şikayət sahəsi boş ola bilməz!")
            return
            
        if not self.diagnosis_input.text().strip():
            QMessageBox.warning(self, "Xəta", "Diaqnoz sahəsi boş ola bilməz!")
            return
            
        # Dərmanları topla
        medications = []
        for row in range(self.medications_table.rowCount()):
            med_name = self.medications_table.item(row, 0)
            dozaj = self.medications_table.item(row, 1)
            qaydalar = self.medications_table.item(row, 2)
            muddet = self.medications_table.item(row, 3)
            
            if med_name and med_name.text().strip():
                medications.append({
                    'ad': med_name.text().strip(),
                    'dozaj': dozaj.text().strip() if dozaj else '',
                    'qaydalar': qaydalar.text().strip() if qaydalar else '',
                    'müddət': muddet.text().strip() if muddet else ''
                })
                
        if not medications:
            QMessageBox.warning(self, "Xəta", "Ən azı bir dərman əlavə etməlisiniz!")
            return
            
        try:
            connection = self.db_manager.get_connection()
            cursor = connection.cursor()
            
            # Resepti əlavə et
            query = """
            INSERT INTO reseptlər (pasiyent_id, həkim_id, şikayət, diaqnoz, dərmanlar, yaradılma_tarixi)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            
            values = (
                self.patient_data['id'],
                self.doctor_id,
                self.complaint_input.toPlainText().strip(),
                self.diagnosis_input.text().strip(),
                json.dumps(medications, ensure_ascii=False),
                datetime.now()
            )
            
            cursor.execute(query, values)
            connection.commit()
            
            cursor.close()
            connection.close()
            
            QMessageBox.information(self, "Uğur", "Resept uğurla yadda saxlanıldı!")
            self.prescription_completed.emit()
            
        except Exception as e:
            QMessageBox.critical(self, "Xəta", f"Resept yadda saxlanarkən xəta: {str(e)}")


class AIAnalysisThread(QThread):
    """AI təhlil thread"""
    
    analysis_completed = pyqtSignal(str)
    
    def __init__(self, ai_assistant, patient_data, history_text):
        super().__init__()
        self.ai_assistant = ai_assistant
        self.patient_data = patient_data
        self.history_text = history_text
        
    def run(self):
        """AI təhlil işini icra et"""
        try:
            prompt = f"""
            Aşağıdakı pasiyent məlumatları və keçmiş reseptlərini təhlil edərək, 
            həkim üçün tövsiyələr hazırla:

            {self.history_text}

            Xahiş edirik:
            1. Keçmiş şikayətlərdə təkrarlanan nümunələri göstərin
            2. Dərman təsirlilik təhlili edin
            3. Yeni resept üçün tövsiyələr verin
            4. Diqqət edilməli məqamları qeyd edin

            Cavabı Azərbaycan dilində və təbib üçün praktik məlumat şəklində verin.
            """
            
            response = self.ai_assistant.get_medical_advice(prompt)
            self.analysis_completed.emit(response)
            
        except Exception as e:
            self.analysis_completed.emit(f"AI təhlil xətası: {str(e)}")