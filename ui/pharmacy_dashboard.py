#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QPushButton, QFrame, QScrollArea, QListWidget,
                            QListWidgetItem, QGridLayout)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPalette, QBrush, QLinearGradient, QColor
from datetime import datetime, date
from ui.fingerprint_scan import FingerprintScanDialog
from ui.sales_dialog import SalesDialog

class PharmacyDashboard(QMainWindow):
    def __init__(self, user_data, db):
        super().__init__()
        self.user_data = user_data
        self.db = db
        self.init_ui()
        self.load_dashboard_data()
        
    def init_ui(self):
        """Dashboard UI-ni hazırla"""
        self.setWindowTitle(f"BioScript Aptek - {self.user_data['pharmacy_name']}")
        self.setGeometry(100, 100, 1200, 800)
        
        # Tam ekran
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.showFullScreen()
        
        # Ana widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Gradient arxa fon
        self.set_gradient_background()
        
        # Ana layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Başlıq
        self.create_header(main_layout)
        
        # Statistika kartları
        self.create_stats_cards(main_layout)
        
        # Alt bölmə - son satışlar və yeni satış
        self.create_bottom_section(main_layout)
        
    def set_gradient_background(self):
        """Gradient arxa fon"""
        palette = self.palette()
        gradient = QLinearGradient(0, 0, 0, 1)
        gradient.setCoordinateMode(QLinearGradient.ObjectBoundingMode)
        gradient.setColorAt(0, QColor(25, 118, 210))
        gradient.setColorAt(1, QColor(13, 71, 161))
        palette.setBrush(QPalette.Window, QBrush(gradient))
        self.setPalette(palette)
        
    def create_header(self, main_layout):
        """Başlıq bölməsini yarat"""
        header_frame = QFrame()
        header_frame.setFixedHeight(80)
        header_frame.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.9);
                border-radius: 15px;
                padding: 15px;
            }
        """)
        
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 10, 20, 10)
        
        # Sol tərəf - məlumat
        left_info = QVBoxLayout()
        
        title_label = QLabel(f"🏥 {self.user_data['pharmacy_name']}")
        title_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title_label.setStyleSheet("color: #1976D2; background: transparent;")
        
        user_label = QLabel(f"İstifadəçi: {self.user_data['name']} ({self.user_data['role']})")
        user_label.setFont(QFont("Segoe UI", 12))
        user_label.setStyleSheet("color: #424242; background: transparent;")
        
        left_info.addWidget(title_label)
        left_info.addWidget(user_label)
        
        # Sağ tərəf - tarix və çıxış
        right_info = QVBoxLayout()
        right_info.setAlignment(Qt.AlignRight)
        
        date_label = QLabel(f"📅 {datetime.now().strftime('%d.%m.%Y - %H:%M')}")
        date_label.setFont(QFont("Segoe UI", 12))
        date_label.setStyleSheet("color: #424242; background: transparent;")
        
        exit_button = QPushButton("ÇIXIŞ")
        exit_button.setFixedSize(80, 35)
        exit_button.setStyleSheet("""
            QPushButton {
                background: #F44336;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover { background: #D32F2F; }
        """)
        exit_button.clicked.connect(self.close)
        
        right_info.addWidget(date_label)
        right_info.addWidget(exit_button)
        
        header_layout.addLayout(left_info)
        header_layout.addStretch()
        header_layout.addLayout(right_info)
        
        main_layout.addWidget(header_frame)
        
    def create_stats_cards(self, main_layout):
        """Statistika kartlarını yarat"""
        stats_frame = QFrame()
        stats_frame.setFixedHeight(200)
        stats_frame.setStyleSheet("background: transparent;")
        
        stats_layout = QGridLayout(stats_frame)
        stats_layout.setSpacing(20)
        
        # Kartlar məlumatı
        cards_data = [
            ("Bu günkü satış", "0.00 ₼", "#4CAF50", "💰"),
            ("Bu aylıq satış", "0.00 ₼", "#2196F3", "📊"),
            ("BioScript-ə borc", f"{self.user_data.get('current_month_commission', 0):.2f} ₼", "#FF9800", "💳"),
            ("Satış sayı", "0", "#9C27B0", "🛒")
        ]
        
        for i, (title, value, color, icon) in enumerate(cards_data):
            card = self.create_stat_card(title, value, color, icon)
            row = i // 2
            col = i % 2
            stats_layout.addWidget(card, row, col)
            
        main_layout.addWidget(stats_frame)
        
    def create_stat_card(self, title, value, color, icon):
        """Statistika kartı yarat"""
        card = QFrame()
        card.setFixedSize(280, 80)
        card.setStyleSheet(f"""
            QFrame {{
                background: rgba(255, 255, 255, 0.9);
                border-radius: 12px;
                border-left: 5px solid {color};
            }}
        """)
        
        layout = QHBoxLayout(card)
        layout.setContentsMargins(15, 10, 15, 10)
        
        # İkon
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI", 24))
        icon_label.setFixedSize(50, 50)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet(f"background: {color}; border-radius: 25px;")
        
        # Mətn bölməsi
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 10))
        title_label.setStyleSheet("color: #666; background: transparent;")
        
        value_label = QLabel(value)
        value_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        value_label.setStyleSheet(f"color: {color}; background: transparent;")
        
        text_layout.addWidget(title_label)
        text_layout.addWidget(value_label)
        
        layout.addWidget(icon_label)
        layout.addLayout(text_layout)
        layout.addStretch()
        
        return card
        
    def create_bottom_section(self, main_layout):
        """Alt bölməni yarat"""
        bottom_frame = QFrame()
        bottom_frame.setStyleSheet("background: transparent;")
        
        bottom_layout = QHBoxLayout(bottom_frame)
        bottom_layout.setSpacing(20)
        
        # Sol tərəf - son satışlar
        self.create_recent_sales(bottom_layout)
        
        # Sağ tərəf - yeni satış düyməsi
        self.create_new_sale_section(bottom_layout)
        
        main_layout.addWidget(bottom_frame)
        
    def create_recent_sales(self, bottom_layout):
        """Son satışlar bölməsini yarat"""
        sales_frame = QFrame()
        sales_frame.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.9);
                border-radius: 15px;
                padding: 20px;
            }
        """)
        
        sales_layout = QVBoxLayout(sales_frame)
        sales_layout.setSpacing(10)
        
        # Başlıq
        sales_title = QLabel("🕒 Son Satış Əməliyyatları")
        sales_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        sales_title.setStyleSheet("color: #1976D2; background: transparent;")
        
        # Siyahı
        self.sales_list = QListWidget()
        self.sales_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                background: white;
                alternate-background-color: #F5F5F5;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #EEEEEE;
            }
            QListWidget::item:selected {
                background: #E3F2FD;
                color: #1976D2;
            }
        """)
        self.sales_list.setAlternatingRowColors(True)
        
        sales_layout.addWidget(sales_title)
        sales_layout.addWidget(self.sales_list)
        
        bottom_layout.addWidget(sales_frame, 2)
        
    def create_new_sale_section(self, bottom_layout):
        """Yeni satış bölməsini yarat"""
        sale_frame = QFrame()
        sale_frame.setFixedWidth(300)
        sale_frame.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.9);
                border-radius: 15px;
                padding: 20px;
            }
        """)
        
        sale_layout = QVBoxLayout(sale_frame)
        sale_layout.setAlignment(Qt.AlignCenter)
        sale_layout.setSpacing(20)
        
        # Başlıq
        sale_title = QLabel("💊 Yeni Satış")
        sale_title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        sale_title.setStyleSheet("color: #1976D2; background: transparent;")
        sale_title.setAlignment(Qt.AlignCenter)
        
        # Böyük satış düyməsi
        new_sale_button = QPushButton("🛒\nYENİ SATIŞ\nBAŞLAT")
        new_sale_button.setFixedSize(200, 120)
        new_sale_button.setFont(QFont("Segoe UI", 12, QFont.Bold))
        new_sale_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4CAF50, stop:1 #388E3C);
                color: white;
                border: none;
                border-radius: 15px;
                font-size: 12pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #66BB6A, stop:1 #4CAF50);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #388E3C, stop:1 #2E7D32);
            }
        """)
        new_sale_button.clicked.connect(self.start_new_sale)
        
        sale_layout.addWidget(sale_title)
        sale_layout.addWidget(new_sale_button)
        sale_layout.addStretch()
        
        bottom_layout.addWidget(sale_frame)
        
    def start_new_sale(self):
        """Yeni satış prosesini başlat"""
        # Əvvəlcə barmaq izi oxuma dialoqu
        fingerprint_dialog = FingerprintScanDialog(self)
        if fingerprint_dialog.exec_() == fingerprint_dialog.Accepted:
            # Aktiv reseptləri göstər
            self.show_sales_dialog()
            
    def show_sales_dialog(self):
        """Satış dialoqunu göstər"""
        sales_dialog = SalesDialog(self.user_data, self.db, self)
        sales_dialog.exec_()
        
        # Dialog bağlandıqdan sonra məlumatları yenilə
        self.load_dashboard_data()
        
    def load_dashboard_data(self):
        """Dashboard məlumatlarını yüklə"""
        if not self.db.connect():
            return
            
        # Bu günkü satışları al
        today = date.today()
        daily_query = """
            SELECT COUNT(*) as count, COALESCE(SUM(total_price), 0) as total
            FROM dispensing_logs 
            WHERE pharmacy_id = %s AND DATE(dispensed_at) = %s
        """
        daily_result = self.db.execute_query(daily_query, (self.user_data['pharmacy_id'], today))
        
        # Bu aylıq satışları al
        month_query = """
            SELECT COUNT(*) as count, COALESCE(SUM(total_price), 0) as total
            FROM dispensing_logs 
            WHERE pharmacy_id = %s AND YEAR(dispensed_at) = %s AND MONTH(dispensed_at) = %s
        """
        month_result = self.db.execute_query(month_query, 
                                           (self.user_data['pharmacy_id'], today.year, today.month))
        
        # Son satışları al
        recent_query = """
            SELECT dl.*, p.name as patient_name 
            FROM dispensing_logs dl
            JOIN patients p ON dl.patient_id = p.id
            WHERE dl.pharmacy_id = %s 
            ORDER BY dl.dispensed_at DESC 
            LIMIT 10
        """
        recent_sales = self.db.execute_query(recent_query, (self.user_data['pharmacy_id'],))
        
        # UI-ni yenilə
        self.update_dashboard_ui(daily_result, month_result, recent_sales)
        
        self.db.disconnect()
        
    def update_dashboard_ui(self, daily_result, month_result, recent_sales):
        """Dashboard UI-ni yenilə"""
        # Bu hissə statistika kartlarını yeniləyəcək
        pass
        
        # Son satışları siyahıya əlavə et
        self.sales_list.clear()
        if recent_sales:
            for sale in recent_sales:
                item_text = f"{sale['patient_name']} - {sale['total_price']:.2f} ₼ ({sale['dispensed_at'].strftime('%d.%m.%Y %H:%M')})"
                item = QListWidgetItem(item_text)
                self.sales_list.addItem(item)
        else:
            item = QListWidgetItem("Hələ ki satış əməliyyatı yoxdur")
            item.setFlags(item.flags() & ~Qt.ItemIsSelectable)
            self.sales_list.addItem(item)
            
    def keyPressEvent(self, event):
        """ESC ilə çıxış"""
        if event.key() == Qt.Key_Escape:
            self.close()
        super().keyPressEvent(event)