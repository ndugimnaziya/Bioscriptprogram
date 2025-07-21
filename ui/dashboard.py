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
# Köhnə fingerprint reader silindi

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
        
        # Statistika kartları - əvvəlcə yaradılır, sonra yenilənir
        self.today_card = self.create_stat_card("Bu Gün", "0", "Resept", "#4caf50")
        layout.addWidget(self.today_card, 0, 0)
        
        self.month_card = self.create_stat_card("Bu Ay", "0", "Resept", "#2196f3")
        layout.addWidget(self.month_card, 0, 1)
        
        self.total_card = self.create_stat_card("Ümumi", "0", "Resept", "#ff9800")
        layout.addWidget(self.total_card, 0, 2)
        
        self.patients_card = self.create_stat_card("Pasiyentlər", "0", "Nəfər", "#9c27b0")
        layout.addWidget(self.patients_card, 0, 3)
        
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
        # Kartı yeniləmək üçün value label-ı saxla
        card.value_label = value_label
        
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
        try:
            # Kartlardakı dəyərləri yenilə
            self.today_card.value_label.setText(str(today_stats.get('total_prescriptions', 0)))
            self.month_card.value_label.setText(str(month_stats.get('total_prescriptions', 0)))
            self.total_card.value_label.setText(str(total_stats.get('total_prescriptions', 0)))
            self.patients_card.value_label.setText(str(total_stats.get('unique_patients', 0)))
            
            print(f"Analitika yeniləndi - Bu gün: {today_stats.get('total_prescriptions', 0)}")
        except Exception as e:
            print(f"Kartları yeniləmə xətası: {e}")
    
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
        layout.setContentsMargins(20, 20, 20, 20)
        
        # BioScript logosu əlavə et
        logo_label = QLabel()
        try:
            from PyQt5.QtGui import QPixmap
            pixmap = QPixmap("./static/bioscript_logo.png")
            if not pixmap.isNull():
                # Loqonu uyğun ölçüyə gətir
                scaled_pixmap = pixmap.scaled(300, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                logo_label.setPixmap(scaled_pixmap)
                logo_label.setAlignment(Qt.AlignCenter)
                logo_label.setStyleSheet("margin: 10px 0; background: transparent;")
                layout.addWidget(logo_label)
            else:
                raise Exception("Logo faylı tapılmadı")
        except Exception as e:
            print(f"Logo yükləmə xətası: {e}")
            # Logo yoxdursa, mətn əlavə et
            logo_text = QLabel("🧬 BioScript")
            logo_text.setFont(QFont("Segoe UI", 24, QFont.Bold))
            logo_text.setAlignment(Qt.AlignCenter)
            logo_text.setStyleSheet("color: #1565c0; margin: 15px 0;")
            layout.addWidget(logo_text)
        layout.setSpacing(10)
        
        # Başlıq
        title = QLabel("🤖 AI Həkim Köməkçisi")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setStyleSheet("color: #1e88e5; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Söhbət tarixi - HTML dəstəyi ilə
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        self.chat_history.setMaximumHeight(300)
        self.chat_history.setHtml("")  # HTML formatında başlat
        self.chat_history.setStyleSheet("""
            QTextEdit {
                border: 2px solid #e3f2fd;
                border-radius: 8px;
                background-color: #fafafa;
                padding: 10px;
                font-family: 'Segoe UI';
                font-size: 12px;
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
        
        # AI başda heç bir şey yazmasın - boş başlasın
        self.chat_history.clear()
        
        # Scroll bar-ın həmişə aşağıda olmasını təmin et
        self.chat_history.verticalScrollBar().setValue(
            self.chat_history.verticalScrollBar().maximum()
        )
        
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
            <div style='background: #1e88e5; color: white; border-radius: 15px; padding: 12px; display: inline-block; max-width: 70%;'>
                {self.format_message_text(message)}
            </div>
            <div style='color: #666; font-size: 10px; margin-top: 5px; text-align: right;'>{current_time}</div>
        </div>
        """
        self.chat_history.insertHtml(formatted_message)
        self.chat_history.verticalScrollBar().setValue(
            self.chat_history.verticalScrollBar().maximum()
        )
        
    def add_ai_message(self, message):
        """AI mesajı əlavə etmə"""
        current_time = datetime.now().strftime("%H:%M")
        formatted_message = f"""
        <div style='margin: 10px 0; text-align: left;'>
            <div style='background: #f5f5f5; color: #333; border-radius: 15px; padding: 12px; display: inline-block; max-width: 70%; border: 1px solid #e0e0e0;'>
                {self.format_message_text(message)}
            </div>
            <div style='color: #666; font-size: 10px; margin-top: 5px;'>{current_time}</div>
        </div>
        """
        self.chat_history.insertHtml(formatted_message)
        self.chat_history.verticalScrollBar().setValue(
            self.chat_history.verticalScrollBar().maximum()
        )
    
    def format_message_text(self, text):
        """Mətni HTML formatına çevirmək - AI markdown-ını düzgün render et"""
        if not text:
            return ""
        
        # Markdown bold **text** -> <strong>text</strong>
        import re
        text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
        
        # Markdown italic *text* -> <em>text</em>
        text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
        
        # Sətir sonları
        text = text.replace('\n', '<br>')
        
        # Dərman adları və dozajlar üçün rəng
        text = re.sub(r'(\d+\s*mg|\d+\s*ml|\d+\s*qram)', r'<span style="color: #ff5722; font-weight: bold;">\1</span>', text)
        
        # Diaqnoz və xəstəlik adları
        text = re.sub(r'(diaqnoz|xəstəlik|sindrom|infeksiya)', r'<span style="color: #2196f3; font-weight: bold;">\1</span>', text, flags=re.IGNORECASE)
        
        return text
    
    def start_fingerprint_workflow(self):
        """Yeni barmaq izi workflow başlatma"""
        try:
            from ui.new_prescription_workflow import FingerprintFirstDialog
            from PyQt5.QtWidgets import QMessageBox
            
            # Əsas widget-in db_manager-ni al
            main_window = self.parent()
            while main_window and not hasattr(main_window, 'db_manager'):
                main_window = main_window.parent()
            
            if main_window and hasattr(main_window, 'db_manager'):
                dialog = FingerprintFirstDialog(main_window.db_manager)
                dialog.fingerprint_success.connect(self.on_fingerprint_success)
                dialog.exec_()
            else:
                QMessageBox.warning(self, "Xəta", "Verilənlər bazası bağlantısı tapılmadı")
            
        except Exception as e:
            print(f"Workflow başlatma xətası: {e}")
    
    def on_fingerprint_success(self, patient_data):
        """Barmaq izi uğurlu oxunduqda"""
        from PyQt5.QtWidgets import QMessageBox
        self.set_patient_context(patient_data, [])
        # Dashboard-da pasiyent məlumatlarını göstər
        QMessageBox.information(self, "Pasiyent Tapıldı", 
                               f"Pasiyent: {patient_data['name']} {patient_data['surname']}\n"
                               f"Telefon: {patient_data.get('phone', 'N/A')}")

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
        # Azərbaycan dilində günlər
        azerbaijani_days = {
            'Monday': 'Bazar ertəsi',
            'Tuesday': 'Çərşənbə axşamı', 
            'Wednesday': 'Çərşənbə',
            'Thursday': 'Cümə axşamı',
            'Friday': 'Cümə',
            'Saturday': 'Şənbə',
            'Sunday': 'Bazar'
        }
        
        current_date = datetime.now()
        date_str = current_date.strftime("%d.%m.%Y")
        day_name_en = current_date.strftime("%A")
        day_name_az = azerbaijani_days.get(day_name_en, day_name_en)
        
        date_label = QLabel(f"{date_str} - {day_name_az}")
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
        
        # Yeni resept düyməsi - Resept tarixçəsi düyməsini sildik, yalnız barmaq izi workflow
        new_prescription_btn = QPushButton("🔬 Yeni Resept Yaz")
        new_prescription_btn.setFixedSize(300, 90)
        new_prescription_btn.setFont(QFont("Segoe UI", 16, QFont.Bold))
        new_prescription_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #4caf50, stop:1 #388e3c);
                color: white;
                border: none;
                border-radius: 15px;
                padding: 20px;
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
        new_prescription_btn.clicked.connect(self.start_fingerprint_workflow)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(new_prescription_btn)
        buttons_layout.addStretch()
        
        parent_layout.addWidget(buttons_frame)
        parent_layout.addStretch()
    
    def start_fingerprint_workflow(self):
        """Yeni streamlined workflow başlatma"""
        try:
            from ui.new_streamlined_workflow import NewStreamlinedWorkflow
            from PyQt5.QtWidgets import QMessageBox
            
            # Yeni workflow yaradırıq
            workflow = NewStreamlinedWorkflow(self.db_manager, self.doctor_data['id'])
            workflow.workflow_completed.connect(self.on_workflow_completed)
            
            # Workflow-u ana pəncərəyə əlavə et
            main_window = self.parent()
            while main_window and not hasattr(main_window, 'central_stack'):
                main_window = main_window.parent()
                
            if main_window and hasattr(main_window, 'central_stack'):
                # Workflow tab əlavə et
                main_window.central_stack.addTab(workflow, "📝 Yeni Resept")
                main_window.central_stack.setCurrentIndex(main_window.central_stack.count() - 1)
                
                # Workflow-u başlat
                workflow.start_workflow()
            else:
                QMessageBox.warning(self, "Xəta", "Ana pəncərə tapılmadı")
            
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Xəta", f"Workflow başlatma xətası: {e}")
            print(f"Workflow başlatma xətası: {e}")
    
    def on_workflow_completed(self):
        """Workflow tamamlandı, dashboard-a qayıt"""
        try:
            main_window = self.parent()
            while main_window and not hasattr(main_window, 'central_stack'):
                main_window = main_window.parent()
                
            if main_window and hasattr(main_window, 'central_stack'):
                # Dashboard tab-ına qayıt
                for i in range(main_window.central_stack.count()):
                    if isinstance(main_window.central_stack.widget(i), BioScriptDashboard):
                        main_window.central_stack.setCurrentIndex(i)
                        break
                        
                # Workflow tab-ını sil
                for i in range(main_window.central_stack.count()):
                    widget = main_window.central_stack.widget(i)
                    if hasattr(widget, 'workflow_completed'):
                        main_window.central_stack.removeTab(i)
                        widget.deleteLater()
                        break
                        
                # Analitikani yenilə
                self.analytics_widget.load_analytics()
                
        except Exception as e:
            print(f"Workflow tamamlanma xətası: {e}")
    
    def set_ai_patient_context(self, patient_data, prescriptions):
        """AI-ya pasiyent kontekstini vermə"""
        self.ai_assistant.set_patient_context(patient_data, prescriptions)