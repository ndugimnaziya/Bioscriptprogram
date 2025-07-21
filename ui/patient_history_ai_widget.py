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
        
        # Sol tərəf - Keçmiş reseptlər və AI köməkçi
        history_frame = QGroupBox("📋 Keçmiş Reseptlər və AI Təhlil")
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
        
        # Keçmiş reseptlər listi - Clickable və professional
        self.history_list = QListWidget()
        self.history_list.itemClicked.connect(self.show_prescription_details)
        self.history_list.setStyleSheet("""
            QListWidget {
                border: 2px solid #e3f2fd;
                border-radius: 12px;
                background: #fafafa;
                padding: 10px;
                font-family: 'Segoe UI';
                font-size: 13px;
            }
            QListWidget::item {
                padding: 15px;
                border: 1px solid #e8f4fd;
                border-radius: 8px;
                margin: 3px 0;
                background: white;
                cursor: pointer;
            }
            QListWidget::item:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #e3f2fd, stop:1 #f0f8ff);
                border: 2px solid #2196f3;
                transform: scale(1.02);
            }
            QListWidget::item:selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #2196f3, stop:1 #1976d2);
                color: white;
                border: 2px solid #1565c0;
                font-weight: bold;
            }
        """)
        
        history_layout.addWidget(self.history_list)
        
        # AI düymələri
        ai_buttons_layout = QHBoxLayout()
        
        self.ai_analyze_btn = QPushButton("🤖 Tarixçə Təhlil Et")
        self.ai_analyze_btn.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.ai_analyze_btn.setFixedHeight(40)
        self.ai_analyze_btn.clicked.connect(self.analyze_with_ai)
        
        self.ai_direct_btn = QPushButton("💡 AI Məsləhət Al")
        self.ai_direct_btn.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.ai_direct_btn.setFixedHeight(40)
        self.ai_direct_btn.clicked.connect(self.get_direct_ai_advice)
        
        # Düymə stilləri
        ai_button_style = """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #ff9800, stop:1 #f57c00);
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                margin: 2px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #ffb74d, stop:1 #ff9800);
            }
            QPushButton:disabled {
                background: #cccccc;
                color: #666666;
            }
        """
        
        self.ai_analyze_btn.setStyleSheet(ai_button_style)
        self.ai_direct_btn.setStyleSheet(ai_button_style)
        
        ai_buttons_layout.addWidget(self.ai_analyze_btn)
        ai_buttons_layout.addWidget(self.ai_direct_btn)
        history_layout.addLayout(ai_buttons_layout)
        
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
        
        # AI tövsiyələri sahəsi - Professional və scroll düzgün işləsin
        ai_label = QLabel("🤖 AI Tövsiyələri və Təhlil:")
        ai_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        ai_label.setStyleSheet("color: #1565c0; margin: 8px 0;")
        
        self.ai_recommendations = QTextEdit()
        self.ai_recommendations.setPlaceholderText("AI təhlil və məsləhət almaq üçün sol tərəfdən düymələrə basın...")
        self.ai_recommendations.setMaximumHeight(180)
        self.ai_recommendations.setReadOnly(True)
        
        # Yeni mesajları altda göstərmək üçün
        self.ai_recommendations.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        self.ai_recommendations.setStyleSheet("""
            QTextEdit {
                border: 2px solid #e3f2fd;
                border-radius: 12px;
                padding: 15px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #f8f9fa, stop:1 #ffffff);
                font-family: 'Segoe UI';
                font-size: 13px;
                color: #2c3e50;
                line-height: 1.5;
            }
            QTextEdit:focus {
                border: 2px solid #2196f3;
                background: white;
            }
            QScrollBar:vertical {
                background: #f0f0f0;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #2196f3;
                border-radius: 6px;
                min-height: 20px;
            }
        """)
        
        prescription_layout.addWidget(ai_label)
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
        
        # Üçüncü bölmə - AI Chat Bölməsi
        chat_frame = QGroupBox("💬 AI Həkim Chat")
        chat_frame.setFont(QFont("Segoe UI", 14, QFont.Bold))
        chat_frame.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e8f5e8;
                border-radius: 10px;
                margin: 10px;
                padding: 15px;
                background: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px;
                color: #2e7d32;
                background: white;
            }
        """)
        
        chat_layout = QVBoxLayout(chat_frame)
        
        # Chat tarixi
        self.chat_history = QTextEdit()
        self.chat_history.setMaximumHeight(300)
        self.chat_history.setReadOnly(True)
        self.chat_history.setStyleSheet("""
            QTextEdit {
                border: 2px solid #e8f5e8;
                border-radius: 8px;
                padding: 10px;
                background: #f9fffe;
                font-family: 'Segoe UI';
                font-size: 12px;
            }
        """)
        
        # Chat input
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("AI həkimə sualınızı yazın...")
        self.chat_input.returnPressed.connect(self.handle_chat_message)
        
        send_chat_btn = QPushButton("Göndər")
        send_chat_btn.clicked.connect(self.handle_chat_message)
        send_chat_btn.setStyleSheet("""
            QPushButton {
                background: #4caf50;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 6px;
                font-weight: bold;
            }
        """)
        
        # Chat input layout
        chat_input_layout = QHBoxLayout()
        chat_input_layout.addWidget(self.chat_input)
        chat_input_layout.addWidget(send_chat_btn)
        
        chat_layout.addWidget(self.chat_history)
        chat_layout.addLayout(chat_input_layout)
        
        main_splitter.addWidget(chat_frame)
        
        # Splitter nisbətləri - 3 hissə üçün
        main_splitter.setSizes([300, 400, 300])
        
        layout.addWidget(main_splitter)
        
    def load_patient_history(self):
        """Pasiyent tarixçəsini yüklə"""
        try:
            connection = self.db_manager.get_connection()
            if not connection or not connection.is_connected():
                QMessageBox.warning(self, "Verilənlər Bazası Xətası", 
                                  "Pasiyent tarixçəsi yoxlanıldı. Connection not available")
                return
            cursor = connection.cursor(dictionary=True)
            
            query = """
            SELECT p.id, p.complaint as şikayət, p.diagnosis as diaqnoz, 
                   '' as dərmanlar, p.issued_at as yaradılma_tarixi,
                   d.name as hekim_adi, d.surname as hekim_soyadi
            FROM prescriptions p
            JOIN doctors d ON p.doctor_id = d.id
            WHERE p.patient_id = %s
            ORDER BY p.issued_at DESC
            LIMIT 10
            """
            
            cursor.execute(query, (self.patient_data['id'],))
            prescriptions = cursor.fetchall()
            
            self.patient_history = []
            self.history_list.clear()
            
            for prescription in prescriptions:
                # Dictionary formatında məlumatları al
                presc_id = prescription['id']
                sikayət = prescription['şikayət'] or ''
                diaqnoz = prescription['diaqnoz'] or ''
                dərmanlar = prescription['dərmanlar'] or ''
                yaradilma = prescription['yaradılma_tarixi']
                hekim_ad = prescription['hekim_adi'] or ''
                hekim_soyad = prescription['hekim_soyadi'] or ''
                
                # Dərmanları parse et
                try:
                    if dərmanlar:
                        meds = json.loads(dərmanlar) if isinstance(dərmanlar, str) else dərmanlar
                    else:
                        meds = []
                except:
                    meds = []
                
                # Tarixi düzgün format et
                yaradilma_obj = yaradilma
                if isinstance(yaradilma, str):
                    # String formatındadırsa parse et
                    try:
                        from datetime import datetime
                        yaradilma_obj = datetime.strptime(yaradilma, '%Y-%m-%d %H:%M:%S')
                        tarix_str = yaradilma_obj.strftime('%d.%m.%Y')
                    except:
                        try:
                            yaradilma_obj = datetime.strptime(yaradilma[:19], '%Y-%m-%d %H:%M:%S')
                            tarix_str = yaradilma_obj.strftime('%d.%m.%Y')
                        except:
                            tarix_str = yaradilma[:10] if len(yaradilma) >= 10 else yaradilma
                            yaradilma_obj = yaradilma
                else:
                    # Datetime obyektidirsə
                    tarix_str = yaradilma.strftime('%d.%m.%Y')
                
                # Tarixçə məlumatlarını saxla
                history_item = {
                    'id': presc_id,
                    'şikayət': sikayət,
                    'diaqnoz': diaqnoz,
                    'dərmanlar': meds,
                    'tarix': yaradilma_obj,
                    'həkim': f"{hekim_ad} {hekim_soyad}"
                }
                self.patient_history.append(history_item)
                
                # List widget-ə əlavə et - həkim adı görünməsin
                item_text = f"""
                📅 {tarix_str}
                🩺 Şikayət: {sikayət[:50]}{'...' if len(sikayət) > 50 else ''}
                🔬 Diaqnoz: {diaqnoz[:50]}{'...' if len(diaqnoz) > 50 else ''}
                💊 Dərman sayı: {len(meds)}
                """
                
                item = QListWidgetItem(item_text.strip())
                item.setData(Qt.UserRole, history_item)
                self.history_list.addItem(item)
                
            cursor.close()
            
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
    
    def get_direct_ai_advice(self):
        """Birbaşa AI məsləhət al (tarixçə olmadan)"""
        self.ai_direct_btn.setEnabled(False)
        self.ai_direct_btn.setText("💡 Məsləhət alınır...")
        
        # Hazırkı şikayət və diaqnoz məlumatlarını al
        complaint = self.complaint_input.toPlainText().strip()
        diagnosis = self.diagnosis_input.text().strip()
        
        if not complaint and not diagnosis:
            QMessageBox.information(self, "Məlumat", 
                                  "Məsləhət almaq üçün şikayət və ya diaqnoz yazın.")
            self.ai_direct_btn.setEnabled(True)
            self.ai_direct_btn.setText("💡 AI Məsləhət Al")
            return
        
        # AI üçün prompt hazırla
        direct_prompt = f"""
        Pasiyent: {self.patient_data['ad']} {self.patient_data['soyad']}, Yaş: {self.patient_data['yaş']}
        
        Şikayət: {complaint if complaint else 'Qeyd edilməyib'}
        Diaqnoz: {diagnosis if diagnosis else 'Qeyd edilməyib'}
        
        Bu məlumatlara əsasən həkim üçün praktik məsləhət verin:
        1. Müalicə yanaşması
        2. Tövsiyə edilən dərmanlar
        3. Diqqət edilməli məqamlar
        4. Əlavə müayinə tövsiyələri
        
        Cavabı Azərbaycan dilində, qısa və aydın təqdim edin.
        """
        
        # AI təhlil thread-də işə sal
        self.ai_direct_thread = AIAnalysisThread(self.ai_assistant, self.patient_data, direct_prompt)
        self.ai_direct_thread.analysis_completed.connect(self.on_direct_ai_completed)
        self.ai_direct_thread.start()
        
    def prepare_history_for_ai(self):
        """AI üçün tarixçə mətnini hazırla"""
        history_text = f"Pasiyent: {self.patient_data['ad']} {self.patient_data['soyad']}, Yaş: {self.patient_data['yaş']}\n\n"
        history_text += "KEÇMİŞ RESEPTLƏRİ:\n"
        
        for i, item in enumerate(self.patient_history, 1):
            # Tarixi düzgün format et
            try:
                if isinstance(item['tarix'], str):
                    tarix_str = item['tarix'][:10]
                else:
                    tarix_str = item['tarix'].strftime('%d.%m.%Y')
            except:
                tarix_str = "Bilinmir"
            
            history_text += f"\n{i}. Resept ({tarix_str}):\n"
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
        self.ai_analyze_btn.setText("🤖 Tarixçə Təhlil Et")
        
        if analysis_result:
            # Yeni mesajı append et və aşağı scroll et
            current_text = self.ai_recommendations.toPlainText()
            if current_text:
                new_text = current_text + "\n\n" + "="*50 + "\n🤖 TARIXÇƏ TƏHLİL NƏTİCƏSİ\n" + "="*50 + "\n" + analysis_result
            else:
                new_text = "🤖 TARIXÇƏ TƏHLİL NƏTİCƏSİ\n" + "="*50 + "\n" + analysis_result
            
            self.ai_recommendations.setPlainText(new_text)
            # Aşağı scroll et
            scrollbar = self.ai_recommendations.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
        else:
            self.ai_recommendations.append("\n❌ AI təhlil zamanı xəta baş verdi.")
    
    def on_direct_ai_completed(self, analysis_result):
        """Birbaşa AI məsləhət tamamlandı"""
        self.ai_direct_btn.setEnabled(True)
        self.ai_direct_btn.setText("💡 AI Məsləhət Al")
        
        if analysis_result:
            # Yeni mesajı append et və aşağı scroll et
            current_text = self.ai_recommendations.toPlainText()
            if current_text:
                new_text = current_text + "\n\n" + "="*50 + "\n💡 AI MƏSLƏHƏT\n" + "="*50 + "\n" + analysis_result
            else:
                new_text = "💡 AI MƏSLƏHƏT\n" + "="*50 + "\n" + analysis_result
            
            self.ai_recommendations.setPlainText(new_text)
            # Aşağı scroll et
            scrollbar = self.ai_recommendations.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
        else:
            self.ai_recommendations.append("\n❌ AI məsləhət zamanı xəta baş verdi.")
    
    def show_prescription_details(self, item):
        """Resept detallarını göstər"""
        history_data = item.data(Qt.UserRole)
        if history_data:
            # Detallı məlumat dialog açaq
            details = f"""
📋 RESEPT DETALLARI

📅 Tarix: {history_data['tarix'].strftime('%d.%m.%Y %H:%M') if hasattr(history_data['tarix'], 'strftime') else str(history_data['tarix'])}
👨‍⚕️ Həkim: {history_data['həkim']}

🩺 ŞİKAYƏT:
{history_data['şikayət']}

🔬 DİAQNOZ:
{history_data['diaqnoz']}

💊 DƏRMANLAR:
"""
            
            for i, med in enumerate(history_data['dərmanlar'], 1):
                if isinstance(med, dict):
                    details += f"{i}. {med.get('ad', 'Bilinməyən')}\n"
                    details += f"   Dozaj: {med.get('dozaj', 'Qeyd edilməyib')}\n"
                    details += f"   Qaydalar: {med.get('qaydalar', 'Qeyd edilməyib')}\n"
                    details += f"   Müddət: {med.get('müddət', 'Qeyd edilməyib')}\n\n"
                else:
                    details += f"{i}. {med}\n\n"
            
            QMessageBox.information(self, "Resept Detalları", details)
    
    def handle_chat_message(self):
        """Chat mesajı göndər"""
        message = self.chat_input.text().strip()
        if not message:
            return
        
        # İstifadəçi mesajını əlavə et
        self.add_chat_message("Siz", message, "#e3f2fd")
        self.chat_input.clear()
        
        # AI cavabını al
        prompt = f"""
        Pasiyent: {self.patient_data['ad']} {self.patient_data['soyad']}, Yaş: {self.patient_data['yaş']}
        
        Həkim sualı: {message}
        
        Bu suala professional həkim kimi cavab verin. Azərbaycan dilində qısa və aydın olsun.
        """
        
        try:
            response = self.ai_assistant.get_response(prompt)
            self.add_chat_message("AI Həkim", response, "#e8f5e8")
        except Exception as e:
            self.add_chat_message("AI Həkim", f"Xəta: {str(e)}", "#ffebee")
    
    def add_chat_message(self, sender, message, bg_color):
        """Chat mesajı əlavə et"""
        current_time = datetime.now().strftime("%H:%M")
        
        # HTML formatında mesaj əlavə et
        html_message = f"""
        <div style='margin: 8px 0; background: {bg_color}; border-radius: 8px; padding: 10px;'>
            <strong>{sender}</strong> <small style='color: #666;'>{current_time}</small><br>
            {message}
        </div>
        """
        
        self.chat_history.append(html_message)
        
        # Aşağı scroll et
        scrollbar = self.chat_history.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
            
    def add_medication_row(self):
        """Dərman cədvəlinə yeni sətir əlavə et"""
        row_count = self.medications_table.rowCount()
        self.medications_table.insertRow(row_count)
        
        # Hər sütun üçün düzenlenə bilən item əlavə et
        for col in range(4):
            item = QTableWidgetItem("")
            item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsEnabled)
            self.medications_table.setItem(row_count, col, item)
        
        # Cədvəli update et və görünürlüyü təmin et
        self.medications_table.resizeColumnsToContents()
        self.medications_table.scrollToBottom()
            
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
            if not connection or not connection.is_connected():
                QMessageBox.critical(self, "Verilənlər Bazası Xətası", 
                                   "Verilənlər bazasına bağlantı yoxdur!")
                return
            cursor = connection.cursor(dictionary=True)
            
            # Resepti əlavə et
            # İlk növbədə prescription yaradırıq
            prescription_query = """
            INSERT INTO prescriptions (patient_id, doctor_id, hospital_id, complaint, diagnosis, issued_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            
            # Prescription əlavə et
            prescription_values = (
                self.patient_data['id'],
                self.doctor_id,
                6,  # Naxçıvan Dövlət Universitetinin Xəstəxanası
                self.complaint_input.toPlainText().strip(),
                self.diagnosis_input.text().strip(),
                datetime.now()
            )
            
            cursor.execute(prescription_query, prescription_values)
            prescription_id = cursor.lastrowid
            
            # Hər dərman üçün prescription_items əlavə et
            if medications:
                item_query = """
                INSERT INTO prescription_items (prescription_id, name, dosage, instructions)
                VALUES (%s, %s, %s, %s)
                """
                
                for med in medications:
                    # SQL cədvəlinə uyğun formatda məlumatları hazırla
                    instructions = med['qaydalar']
                    if med['müddət']:
                        instructions += f" - {med['müddət']}"
                    
                    item_values = (
                        prescription_id,
                        med['ad'],
                        med['dozaj'],
                        instructions
                    )
                    cursor.execute(item_query, item_values)
            
            connection.commit()
            
            cursor.close()
            
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
            
            response = self.ai_assistant.get_response(prompt)
            self.analysis_completed.emit(response)
            
        except Exception as e:
            self.analysis_completed.emit(f"AI təhlil xətası: {str(e)}")