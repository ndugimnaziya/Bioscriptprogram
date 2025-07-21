#!/usr/bin/env python3
"""
BioScript - Həkim Dashboard
Analitika, resept tarixçəsi və AI köməkçisi
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QFrame, QGridLayout, QListWidget,
                            QTextEdit, QLineEdit, QScrollArea, QSplitter,
                            QGroupBox, QListWidgetItem, QProgressBar,
                            QTabWidget, QTableWidget, QTableWidgetItem)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QColor, QPalette
from datetime import datetime, date, timedelta
import threading

from gemini_ai import BioScriptAI
from fingerprint_reader import FingerprintSimulator

class AnalyticsWidget(QWidget):
    """Analitika kartları"""
    
    def __init__(self, db_manager, doctor_id):
        super().__init__()
        self.db_manager = db_manager
        self.doctor_id = doctor_id
        self.init_ui()
        self.load_analytics()
        
    def init_ui(self):
        """Analitika UI yaratma"""
        layout = QGridLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Bugünkü reseptlər
        today_card = self.create_stat_card("Bu gün", "0", "resept", "#4caf50")
        layout.addWidget(today_card, 0, 0)
        
        # Bu ay
        month_card = self.create_stat_card("Bu ay", "0", "resept", "#2196f3")
        layout.addWidget(month_card, 0, 1)
        
        # Ümumi
        total_card = self.create_stat_card("Ümumi", "0", "resept", "#ff9800")
        layout.addWidget(total_card, 0, 2)
        
        # Pasiyent sayı
        patients_card = self.create_stat_card("Pasiyentlər", "0", "nəfər", "#9c27b0")
        layout.addWidget(patients_card, 0, 3)
        
        # Son reseptlər
        recent_frame = QGroupBox("Son Reseptlər")
        recent_frame.setFont(QFont("Segoe UI", 14, QFont.Bold))
        recent_frame.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e3f2fd;
                border-radius: 10px;
                margin: 15px 0;
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
        recent_layout = QVBoxLayout(recent_frame)
        
        self.recent_list = QListWidget()
        self.recent_list.setMaximumHeight(250)
        self.recent_list.setStyleSheet("""
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
                background: #f5f5f5;
            }
            QListWidget::item:selected {
                background: #e3f2fd;
                color: #1565c0;
            }
        """)
        recent_layout.addWidget(self.recent_list)
        
        layout.addWidget(recent_frame, 1, 0, 1, 4)
        
    def create_stat_card(self, title, value, unit, color):
        """Statistika kartı yaratma"""
        card = QFrame()
        card.setFixedSize(220, 140)
        card.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                          stop:0 {color}, stop:1 {color}dd);
                border-radius: 15px;
                border: none;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                margin: 5px;
            }}
            QFrame:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                          stop:0 {color}ee, stop:1 {color}ff);
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 15, 15, 15)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 13, QFont.Bold))
        title_label.setStyleSheet("color: rgba(255,255,255,0.9); margin-bottom: 5px;")
        
        value_label = QLabel(value)
        value_label.setFont(QFont("Segoe UI", 36, QFont.Bold))
        value_label.setStyleSheet("color: white; margin: 10px 0;")
        value_label.setAlignment(Qt.AlignCenter)
        
        unit_label = QLabel(unit)
        unit_label.setFont(QFont("Segoe UI", 11))
        unit_label.setStyleSheet("color: rgba(255,255,255,0.8);")
        unit_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        layout.addWidget(unit_label)
        
        return card
        
    def load_analytics(self):
        """Analitika məlumatlarını yükləmə"""
        try:
            today = date.today()
            month_start = today.replace(day=1)
            
            # Bu günkü reseptlər
            stats = self.db_manager.get_doctor_statistics(
                self.doctor_id, today, today
            )
            
            # Bu ayın reseptləri
            month_stats = self.db_manager.get_doctor_statistics(
                self.doctor_id, month_start, today
            )
            
            # Ümumi reseptlər
            total_stats = self.db_manager.get_doctor_statistics(self.doctor_id)
            
            # Kartları yenilə
            self.update_stat_cards(stats, month_stats, total_stats)
            
            # Son reseptləri yüklə
            self.load_recent_prescriptions()
            
        except Exception as e:
            print(f"Analitika yükləmə xətası: {e}")
    
    def update_stat_cards(self, today_stats, month_stats, total_stats):
        """Statistika kartlarını yeniləmə"""
        # İlk card-ın value label-ını tapıb yenilə
        # Bu daha mürəkkəb implementation tələb edir
        # Sadəlik üçün print edəcək
        print(f"Bu gün: {today_stats.get('total_prescriptions', 0)}")
        print(f"Bu ay: {month_stats.get('total_prescriptions', 0)}")
        print(f"Ümumi: {total_stats.get('total_prescriptions', 0)}")
        print(f"Pasiyentlər: {total_stats.get('unique_patients', 0)}")
    
    def load_recent_prescriptions(self):
        """Son reseptləri yükləmə"""
        try:
            # Son 10 resepti al
            query = """
            SELECT p.*, pt.name as patient_name, DATE(p.issued_at) as date
            FROM prescriptions p
            JOIN patients pt ON p.patient_id = pt.id
            WHERE p.doctor_id = %s
            ORDER BY p.issued_at DESC
            LIMIT 10
            """
            
            self.db_manager.cursor.execute(query, (self.doctor_id,))
            prescriptions = self.db_manager.cursor.fetchall()
            
            self.recent_list.clear()
            for prescription in prescriptions:
                item_text = f"{prescription['patient_name']} - {prescription['date']}"
                if prescription['diagnosis']:
                    item_text += f" - {prescription['diagnosis'][:30]}..."
                
                item = QListWidgetItem(item_text)
                self.recent_list.addItem(item)
                
        except Exception as e:
            print(f"Son reseptlər yükləmə xətası: {e}")

class AIAssistantWidget(QWidget):
    """Gemini AI köməkçisi"""
    
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.ai = BioScriptAI()
        self.current_patient = None
        self.current_doctor = None
        self.init_ui()
        
    def init_ui(self):
        """AI köməkçi UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Başlıq
        title = QLabel("🤖 AI Həkim Köməkçisi")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setStyleSheet("color: #1e88e5; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Söhbət tarixi
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        self.chat_history.setMaximumHeight(300)
        self.chat_history.setStyleSheet("""
            QTextEdit {
                border: 2px solid #e3f2fd;
                border-radius: 8px;
                background-color: #fafafa;
                padding: 10px;
            }
        """)
        layout.addWidget(self.chat_history)
        
        # Sual input
        input_layout = QHBoxLayout()
        
        self.question_input = QLineEdit()
        self.question_input.setPlaceholderText("AI-dan sual verin...")
        self.question_input.returnPressed.connect(self.send_question)
        
        send_btn = QPushButton("Göndər")
        send_btn.clicked.connect(self.send_question)
        send_btn.setFixedWidth(80)
        
        input_layout.addWidget(self.question_input)
        input_layout.addWidget(send_btn)
        layout.addLayout(input_layout)
        
        # Sürətli düymələr
        quick_buttons_layout = QHBoxLayout()
        
        analyze_btn = QPushButton("Pasiyent Analizi")
        analyze_btn.clicked.connect(self.analyze_patient)
        
        suggest_btn = QPushButton("Müalicə Təklifi")
        suggest_btn.clicked.connect(self.suggest_treatment)
        
        quick_buttons_layout.addWidget(analyze_btn)
        quick_buttons_layout.addWidget(suggest_btn)
        layout.addLayout(quick_buttons_layout)
        
        # Xoş gəldin mesajı
        self.add_ai_message("Salam! Mən sizin AI həkim köməkçinizəm. Sizə necə kömək edə bilərəm?")
        
    def set_patient_context(self, patient_data, prescriptions):
        """Pasiyent kontekstini təyin etmə"""
        self.current_patient = patient_data
        self.current_prescriptions = prescriptions
        
        patient_name = patient_data.get('name', 'N/A')
        self.add_ai_message(f"✅ {patient_name} pasiyentinin məlumatları yükləndi. Analiz üçün hazıram!")
        
    def send_question(self):
        """Sual göndərmə"""
        question = self.question_input.text().strip()
        if not question:
            return
            
        self.add_user_message(question)
        self.question_input.clear()
        
        # AI cavabını başqa thread-də al
        threading.Thread(target=self.get_ai_response, args=(question,), daemon=True).start()
        
    def get_ai_response(self, question):
        """AI cavabını alma"""
        try:
            context = ""
            if self.current_patient:
                context = f"Hal-hazırdakı pasiyent: {self.current_patient.get('name', 'N/A')}"
                
            response = self.ai.chat_with_doctor(question, context)
            self.add_ai_message(response)
            
        except Exception as e:
            self.add_ai_message(f"Xəta: {str(e)}")
    
    def analyze_patient(self):
        """Pasiyent analizi"""
        if not self.current_patient:
            self.add_ai_message("⚠️ Analiz üçün əvvəlcə pasiyent seçin.")
            return
            
        self.add_user_message("🔍 Pasiyent analizi tələb edilir")
        
        threading.Thread(target=self.perform_analysis, daemon=True).start()
        
    def perform_analysis(self):
        """Analizi həyata keçirmə"""
        try:
            prescriptions = getattr(self, 'current_prescriptions', [])
            analysis = self.ai.analyze_patient_history(self.current_patient, prescriptions)
            self.add_ai_message(f"📊 **Pasiyent Analizi:**\n\n{analysis}")
            
        except Exception as e:
            self.add_ai_message(f"Analiz xətası: {str(e)}")
    
    def suggest_treatment(self):
        """Müalicə təklifi"""
        if not self.current_patient:
            self.add_ai_message("⚠️ Müalicə təklifi üçün əvvəlcə pasiyent seçin.")
            return
            
        # Sadə input dialog - real implementasiyada daha inkişaf etmiş olmalı
        complaint = "Baş ağrısı və yüksək temperatur"  # Test üçün
        
        self.add_user_message(f"💊 Müalicə təklifi: {complaint}")
        
        threading.Thread(target=self.get_treatment_suggestion, args=(complaint,), daemon=True).start()
        
    def get_treatment_suggestion(self, complaint):
        """Müalicə təklifini alma"""
        try:
            history = ""
            if hasattr(self, 'current_prescriptions'):
                history = str(self.current_prescriptions)
                
            suggestion = self.ai.get_treatment_suggestion(complaint, "", history)
            self.add_ai_message(f"💊 **Müalicə Təklifi:**\n\n{suggestion}")
            
        except Exception as e:
            self.add_ai_message(f"Müalicə təklifi xətası: {str(e)}")
    
    def add_user_message(self, message):
        """İstifadəçi mesajı əlavə etmə"""
        current_time = datetime.now().strftime("%H:%M")
        formatted_message = f"""
        <div style='margin: 10px 0; text-align: right;'>
            <div style='background: #1e88e5; color: white; border-radius: 15px; padding: 10px; display: inline-block; max-width: 70%;'>
                {message}
            </div>
            <div style='color: #666; font-size: 10px; margin-top: 5px;'>{current_time}</div>
        </div>
        """
        self.chat_history.append(formatted_message)
        
    def add_ai_message(self, message):
        """AI mesajı əlavə etmə"""
        current_time = datetime.now().strftime("%H:%M")
        formatted_message = f"""
        <div style='margin: 10px 0; text-align: left;'>
            <div style='background: #f5f5f5; color: #333; border-radius: 15px; padding: 10px; display: inline-block; max-width: 70%; border: 1px solid #e0e0e0;'>
                {message}
            </div>
            <div style='color: #666; font-size: 10px; margin-top: 5px;'>{current_time}</div>
        </div>
        """
        self.chat_history.append(formatted_message)

class BioScriptDashboard(QWidget):
    """Əsas dashboard"""
    
    new_prescription_requested = pyqtSignal()
    view_prescriptions_requested = pyqtSignal()
    
    def __init__(self, db_manager, doctor_data):
        super().__init__()
        self.db_manager = db_manager
        self.doctor_data = doctor_data
        self.init_ui()
        
    def init_ui(self):
        """Dashboard UI yaratma"""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sol tərəf - Əsas dashboard
        left_frame = QFrame()
        left_frame.setMinimumWidth(800)
        left_layout = QVBoxLayout(left_frame)
        left_layout.setContentsMargins(20, 20, 20, 20)
        left_layout.setSpacing(20)
        
        # Header
        self.create_header(left_layout)
        
        # Analitika
        self.analytics_widget = AnalyticsWidget(self.db_manager, self.doctor_data['id'])
        left_layout.addWidget(self.analytics_widget)
        
        # Əsas düymələr
        self.create_action_buttons(left_layout)
        
        # Sağ tərəf - AI köməkçisi
        right_frame = QFrame()
        right_frame.setFixedWidth(450)
        right_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #ffffff, stop:1 #f8f9fa);
                border-left: 3px solid #e3f2fd;
                border-radius: 0 15px 15px 0;
            }
        """)
        
        right_layout = QVBoxLayout(right_frame)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        self.ai_assistant = AIAssistantWidget(self.db_manager)
        right_layout.addWidget(self.ai_assistant)
        
        # Splitter
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_frame)
        splitter.addWidget(right_frame)
        splitter.setSizes([800, 400])
        
        main_layout.addWidget(splitter)
        
    def create_header(self, parent_layout):
        """Header yaratma"""
        header_frame = QFrame()
        header_frame.setFixedHeight(80)
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                          stop:0 #1e88e5, stop:1 #1976d2);
                border-radius: 15px;
                box-shadow: 0 4px 12px rgba(30,136,229,0.3);
            }
        """)
        
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 15, 20, 15)
        
        # Xoş gəlmisiniz
        welcome_label = QLabel(f"Xoş gəlmisiniz, Dr. {self.doctor_data['name']} {self.doctor_data['surname']}")
        welcome_label.setFont(QFont("Segoe UI", 20, QFont.Bold))
        welcome_label.setStyleSheet("color: white; padding: 5px;")
        
        # Tarix
        date_label = QLabel(datetime.now().strftime("%d.%m.%Y - %A"))
        date_label.setFont(QFont("Segoe UI", 13))
        date_label.setStyleSheet("color: rgba(255,255,255,0.9); padding: 5px;")
        date_label.setAlignment(Qt.AlignRight)
        
        header_layout.addWidget(welcome_label)
        header_layout.addStretch()
        header_layout.addWidget(date_label)
        
        parent_layout.addWidget(header_frame)
        
    def create_action_buttons(self, parent_layout):
        """Əsas funksiya düymələri"""
        buttons_frame = QGroupBox("Əsas Funksiyalar")
        buttons_frame.setFont(QFont("Segoe UI", 16, QFont.Bold))
        buttons_frame.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e3f2fd;
                border-radius: 15px;
                margin: 20px 0;
                padding: 20px;
                background: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 20px;
                padding: 0 15px;
                color: #1565c0;
                background: white;
            }
        """)
        buttons_layout = QHBoxLayout(buttons_frame)
        buttons_layout.setSpacing(30)
        
        # Yeni resept düyməsi
        new_prescription_btn = QPushButton("🔬 Yeni Resept Yaz")
        new_prescription_btn.setFixedSize(240, 90)
        new_prescription_btn.setFont(QFont("Segoe UI", 15, QFont.Bold))
        new_prescription_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #4caf50, stop:1 #388e3c);
                color: white;
                border: none;
                border-radius: 15px;
                padding: 15px;
                box-shadow: 0 4px 8px rgba(76,175,80,0.3);
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #66bb6a, stop:1 #4caf50);
                transform: translateY(-2px);
            }
            QPushButton:pressed {
                transform: translateY(0px);
            }
        """)
        new_prescription_btn.clicked.connect(self.new_prescription_requested.emit)
        
        # Resept tarixçəsi düyməsi
        view_prescriptions_btn = QPushButton("📋 Resept Tarixçəsi")
        view_prescriptions_btn.setFixedSize(240, 90)
        view_prescriptions_btn.setFont(QFont("Segoe UI", 15, QFont.Bold))
        view_prescriptions_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #2196f3, stop:1 #1976d2);
                color: white;
                border: none;
                border-radius: 15px;
                padding: 15px;
                box-shadow: 0 4px 8px rgba(33,150,243,0.3);
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #42a5f5, stop:1 #2196f3);
                transform: translateY(-2px);
            }
            QPushButton:pressed {
                transform: translateY(0px);
            }
        """)
        view_prescriptions_btn.clicked.connect(self.view_prescriptions_requested.emit)
        
        buttons_layout.addWidget(new_prescription_btn)
        buttons_layout.addWidget(view_prescriptions_btn)
        buttons_layout.addStretch()
        
        parent_layout.addWidget(buttons_frame)
        parent_layout.addStretch()
    
    def set_ai_patient_context(self, patient_data, prescriptions):
        """AI-ya pasiyent kontekstini vermə"""
        self.ai_assistant.set_patient_context(patient_data, prescriptions)