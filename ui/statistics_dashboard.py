"""
BioScript - Statistika Dashboard
Həkim statistikaları və analitika interfeysi
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QFrame, QGroupBox, QGridLayout, QTableWidget,
                            QTableWidgetItem, QComboBox, QDateEdit, 
                            QPushButton, QTextEdit, QScrollArea,
                            QProgressBar, QSizePolicy)
from PyQt5.QtCore import Qt, QDate, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor
from datetime import datetime, timedelta

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

class StatisticsLoadThread(QThread):
    """Statistika yükləmə thread"""
    
    statistics_loaded = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, db_manager, doctor_id, start_date=None, end_date=None):
        super().__init__()
        self.db_manager = db_manager
        self.doctor_id = doctor_id
        self.start_date = start_date
        self.end_date = end_date
    
    def run(self):
        try:
            stats = self.db_manager.get_doctor_statistics(
                self.doctor_id, self.start_date, self.end_date
            )
            self.statistics_loaded.emit(stats)
        except Exception as e:
            self.error_occurred.emit(str(e))

class StatisticsDashboard(QWidget):
    """Statistika dashboard widget"""
    
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.current_doctor_id = None
        self.current_stats = {}
        
        self.init_ui()
    
    def init_ui(self):
        """İstifadəçi interfeysi başlatma"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        
        # Başlıq və filtr
        self.create_header_section(main_layout)
        
        # Statistika kartları
        self.create_stats_cards(main_layout)
        
        # Qrafiklər və cədvəllər
        content_layout = QHBoxLayout()
        
        # Sol tərəf - qrafiklər
        if MATPLOTLIB_AVAILABLE:
            self.create_charts_section(content_layout)
        
        # Sağ tərəf - cədvəllər
        self.create_tables_section(content_layout)
        
        main_layout.addLayout(content_layout)
        
        # Başlanğıc vəziyyət
        self.show_no_data_message()
    
    def create_header_section(self, parent_layout):
        """Başlıq və filtr hissəsi"""
        header_frame = QFrame()
        header_frame.setFrameStyle(QFrame.Box)
        header_layout = QVBoxLayout(header_frame)
        
        # Başlıq
        title_label = QLabel("📊 Həkim Statistikaları")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setStyleSheet("color: #2c3e50; padding: 10px;")
        header_layout.addWidget(title_label)
        
        # Filtr sətri
        filter_layout = QHBoxLayout()
        
        # Tarix filtri
        filter_layout.addWidget(QLabel("Başlanğıc tarixi:"))
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setDate(QDate.currentDate().addDays(-30))
        self.start_date_edit.setCalendarPopup(True)
        filter_layout.addWidget(self.start_date_edit)
        
        filter_layout.addWidget(QLabel("Bitmə tarixi:"))
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setDate(QDate.currentDate())
        self.end_date_edit.setCalendarPopup(True)
        filter_layout.addWidget(self.end_date_edit)
        
        # Yenilə düyməsi
        refresh_btn = QPushButton("🔄 Yenilə")
        refresh_btn.clicked.connect(self.refresh_statistics)
        filter_layout.addWidget(refresh_btn)
        
        filter_layout.addStretch()
        
        # Export düyməsi
        export_btn = QPushButton("📤 İxrac et")
        export_btn.clicked.connect(self.export_statistics)
        filter_layout.addWidget(export_btn)
        
        header_layout.addLayout(filter_layout)
        parent_layout.addWidget(header_frame)
    
    def create_stats_cards(self, parent_layout):
        """Statistika kartları"""
        cards_frame = QFrame()
        cards_layout = QGridLayout(cards_frame)
        cards_layout.setSpacing(15)
        
        # Kart stilləri
        card_style = """
        QFrame {
            background-color: white;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 15px;
        }
        """
        
        # Ümumi reseptlər kartı
        self.total_prescriptions_card = self.create_stat_card(
            "📋", "Ümumi Reseptlər", "0", "#007bff", card_style
        )
        cards_layout.addWidget(self.total_prescriptions_card, 0, 0)
        
        # Unikal pasiyentlər kartı
        self.unique_patients_card = self.create_stat_card(
            "👥", "Unikal Pasiyentlər", "0", "#28a745", card_style
        )
        cards_layout.addWidget(self.unique_patients_card, 0, 1)
        
        # Orta resept sayı kartı
        self.avg_prescriptions_card = self.create_stat_card(
            "📊", "Günlük Orta", "0", "#ffc107", card_style
        )
        cards_layout.addWidget(self.avg_prescriptions_card, 0, 2)
        
        # Bu ay kartı
        self.monthly_card = self.create_stat_card(
            "📅", "Bu Ay", "0", "#17a2b8", card_style
        )
        cards_layout.addWidget(self.monthly_card, 0, 3)
        
        parent_layout.addWidget(cards_frame)
    
    def create_stat_card(self, icon, title, value, color, style):
        """Statistika kartı yaratma"""
        card = QFrame()
        card.setStyleSheet(style)
        card.setMinimumHeight(120)
        
        layout = QVBoxLayout(card)
        
        # İkon və başlıq
        header_layout = QHBoxLayout()
        
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Arial", 24))
        icon_label.setStyleSheet(f"color: {color};")
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        title_label.setStyleSheet("color: #6c757d;")
        
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Dəyər
        value_label = QLabel(value)
        value_label.setFont(QFont("Arial", 28, QFont.Bold))
        value_label.setStyleSheet(f"color: {color};")
        value_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(value_label)
        layout.addStretch()
        
        # Dəyər label-ını card-a əlavə et
        card.value_label = value_label
        
        return card
    
    def create_charts_section(self, parent_layout):
        """Qrafiklər hissəsi"""
        charts_frame = QFrame()
        charts_frame.setFrameStyle(QFrame.Box)
        charts_layout = QVBoxLayout(charts_frame)
        
        # Başlıq
        charts_label = QLabel("📈 Qrafiklər")
        charts_label.setFont(QFont("Arial", 14, QFont.Bold))
        charts_layout.addWidget(charts_label)
        
        # Matplotlib canvas
        self.figure = Figure(figsize=(8, 6))
        self.canvas = FigureCanvas(self.figure)
        charts_layout.addWidget(self.canvas)
        
        parent_layout.addWidget(charts_frame, 2)
    
    def create_tables_section(self, parent_layout):
        """Cədvəllər hissəsi"""
        tables_frame = QFrame()
        tables_frame.setFrameStyle(QFrame.Box)
        tables_layout = QVBoxLayout(tables_frame)
        
        # Ən çox təyin olunan dərmanlar
        meds_label = QLabel("💊 Ən Çox Təyin Olunan Dərmanlar")
        meds_label.setFont(QFont("Arial", 14, QFont.Bold))
        tables_layout.addWidget(meds_label)
        
        self.medications_table = QTableWidget()
        self.medications_table.setColumnCount(2)
        self.medications_table.setHorizontalHeaderLabels(["Dərman Adı", "Sayı"])
        self.medications_table.setMaximumHeight(300)
        
        # Cədvəl sütun genişlikləri
        header = self.medications_table.horizontalHeader()
        header.setStretchLastSection(True)
        
        tables_layout.addWidget(self.medications_table)
        
        # Son aktivlik
        activity_label = QLabel("🕒 Son Aktivlik")
        activity_label.setFont(QFont("Arial", 14, QFont.Bold))
        tables_layout.addWidget(activity_label)
        
        self.activity_text = QTextEdit()
        self.activity_text.setReadOnly(True)
        self.activity_text.setMaximumHeight(200)
        tables_layout.addWidget(self.activity_text)
        
        parent_layout.addWidget(tables_frame, 1)
    
    def show_no_data_message(self):
        """Məlumat yoxdur mesajı"""
        if hasattr(self, 'canvas'):
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            ax.text(0.5, 0.5, 'Həkim girişindən sonra\nstatistikalar göstəriləcək', 
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes, fontsize=14, color='gray')
            ax.set_xticks([])
            ax.set_yticks([])
            self.canvas.draw()
        
        # Dərmanlar cədvəlini təmizlə
        self.medications_table.setRowCount(0)
        
        # Aktivlik mətni
        self.activity_text.setText("Həkim girişindən sonra aktivlik göstəriləcək")
    
    def refresh_data(self, doctor_id):
        """Məlumatları yeniləmə"""
        self.current_doctor_id = doctor_id
        self.refresh_statistics()
    
    def refresh_statistics(self):
        """Statistikaları yeniləmə"""
        if not self.current_doctor_id:
            return
        
        # Tarix filtrləri
        start_date = self.start_date_edit.date().toPyDate()
        end_date = self.end_date_edit.date().toPyDate()
        
        # Thread başlat
        self.stats_thread = StatisticsLoadThread(
            self.db_manager, self.current_doctor_id, start_date, end_date
        )
        self.stats_thread.statistics_loaded.connect(self.on_statistics_loaded)
        self.stats_thread.error_occurred.connect(self.on_statistics_error)
        self.stats_thread.start()
    
    def on_statistics_loaded(self, stats):
        """Statistika yükləndikdə"""
        self.current_stats = stats
        
        # Kartları yenilə
        self.update_stat_cards(stats)
        
        # Cədvəlləri yenilə
        self.update_medications_table(stats.get('top_medications', []))
        
        # Qrafiki yenilə
        if MATPLOTLIB_AVAILABLE:
            self.update_charts(stats)
        
        # Aktivlik mətni
        self.update_activity_text(stats)
    
    def on_statistics_error(self, error_message):
        """Statistika xətası"""
        self.activity_text.setText(f"Statistika yükləmə xətası: {error_message}")
    
    def update_stat_cards(self, stats):
        """Statistika kartlarını yeniləmə"""
        # Ümumi reseptlər
        total = stats.get('total_prescriptions', 0)
        self.total_prescriptions_card.value_label.setText(str(total))
        
        # Unikal pasiyentlər
        unique = stats.get('unique_patients', 0)
        self.unique_patients_card.value_label.setText(str(unique))
        
        # Günlük orta (son 30 gün əsasında)
        if total > 0:
            days_diff = (self.end_date_edit.date().toPyDate() - 
                        self.start_date_edit.date().toPyDate()).days
            avg = round(total / max(days_diff, 1), 1)
            self.avg_prescriptions_card.value_label.setText(str(avg))
        else:
            self.avg_prescriptions_card.value_label.setText("0")
        
        # Bu ay (placeholder)
        self.monthly_card.value_label.setText(str(total))
    
    def update_medications_table(self, medications):
        """Dərmanlar cədvəlini yeniləmə"""
        self.medications_table.setRowCount(len(medications))
        
        for row, med in enumerate(medications):
            self.medications_table.setItem(row, 0, QTableWidgetItem(med['medication_name']))
            self.medications_table.setItem(row, 1, QTableWidgetItem(str(med['count'])))
        
        self.medications_table.resizeColumnsToContents()
    
    def update_charts(self, stats):
        """Qrafiklə yeniləmə"""
        self.figure.clear()
        
        # Top medications bar chart
        medications = stats.get('top_medications', [])
        
        if medications:
            ax = self.figure.add_subplot(111)
            
            # Məlumatları hazırla
            names = [med['medication_name'][:15] + '...' if len(med['medication_name']) > 15 
                    else med['medication_name'] for med in medications[:10]]
            counts = [med['count'] for med in medications[:10]]
            
            # Bar chart
            bars = ax.bar(range(len(names)), counts, color='#007bff', alpha=0.7)
            
            # Qrafik tərtibatı
            ax.set_xlabel('Dərmanlar')
            ax.set_ylabel('Təyin edilmə sayı')
            ax.set_title('Ən Çox Təyin Olunan Dərmanlar')
            ax.set_xticks(range(len(names)))
            ax.set_xticklabels(names, rotation=45, ha='right')
            
            # Dəyərləri bar-ların üstündə göstər
            for bar, count in zip(bars, counts):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                       str(count), ha='center', va='bottom')
            
            self.figure.tight_layout()
        else:
            # Məlumat yoxdur
            ax = self.figure.add_subplot(111)
            ax.text(0.5, 0.5, 'Seçilmiş müddətdə\nməlumat yoxdur', 
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes, fontsize=14, color='gray')
            ax.set_xticks([])
            ax.set_yticks([])
        
        self.canvas.draw()
    
    def update_activity_text(self, stats):
        """Aktivlik mətni yeniləmə"""
        total = stats.get('total_prescriptions', 0)
        unique = stats.get('unique_patients', 0)
        
        activity_html = f"""
        <h4>📊 Statistika Xülasəsi</h4>
        
        <p><b>Seçilmiş müddət:</b><br>
        {self.start_date_edit.date().toString('dd.MM.yyyy')} - 
        {self.end_date_edit.date().toString('dd.MM.yyyy')}</p>
        
        <p><b>Ümumi nəticələr:</b><br>
        • Yazılmış reseptlər: {total}<br>
        • Müayinə edilmiş pasiyentlər: {unique}<br>
        • Orta resept/gün: {round(total/max((self.end_date_edit.date().toPyDate() - self.start_date_edit.date().toPyDate()).days, 1), 1)}</p>
        
        <p><b>Performans:</b><br>
        • {"Yüksək aktivlik" if total > 50 else "Orta aktivlik" if total > 20 else "Aşağı aktivlik"}<br>
        • {"Müxtəlif pasiyent bazası" if unique > 20 else "Məhdud pasiyent bazası"}</p>
        """
        
        self.activity_text.setHtml(activity_html)
    
    def export_statistics(self):
        """Statistikaları ixrac etmə"""
        if not self.current_stats:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(self, "Məlumat", "İxrac etmək üçün statistika yoxdur!")
            return
        
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.information(self, "Məlumat", "İxrac funksiyası hazırlanır...")