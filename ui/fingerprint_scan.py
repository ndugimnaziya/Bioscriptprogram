#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QProgressBar)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPalette, QBrush, QLinearGradient, QColor

class FingerprintScanDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.progress_value = 0
        self.init_ui()
        self.start_fake_scan()
        
    def init_ui(self):
        """Barmaq izi oxuma UI-ni hazırla"""
        self.setWindowTitle("BioScript Barmaq İzi Oxuma")
        self.setFixedSize(650, 500)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        
        # Mərkəzləşdirmək üçün
        if self.parent():
            parent_pos = self.parent().pos()
            parent_size = self.parent().size()
            x = parent_pos.x() + (parent_size.width() - 650) // 2
            y = parent_pos.y() + (parent_size.height() - 500) // 2
            self.move(x, y)
        
        # Gradient arxa fon
        self.set_gradient_background()
        
        # Ana layout
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setSpacing(30)
        main_layout.setContentsMargins(40, 40, 40, 40)
        
        # Başlıq
        title_label = QLabel("🔐 BioScript Barmaq İzi Oxuma")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title_label.setStyleSheet("""
            color: white;
            background: transparent;
            padding: 10px;
        """)
        title_label.setFixedHeight(80)
        
        # Barmaq izi ikonu
        fingerprint_label = QLabel("👆")
        fingerprint_label.setAlignment(Qt.AlignCenter)
        fingerprint_label.setFont(QFont("Segoe UI", 96))
        fingerprint_label.setStyleSheet("""
            color: white;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 90px;
            padding: 20px;
        """)
        fingerprint_label.setFixedSize(180, 180)
        
        # Status yazısı
        self.status_label = QLabel("Barmağınızı oxuyucu üzərinə qoyun...")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFont(QFont("Segoe UI", 14))
        self.status_label.setStyleSheet("""
            color: #E3F2FD;
            background: transparent;
            padding: 10px;
        """)
        self.status_label.setFixedHeight(70)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(25)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid white;
                border-radius: 12px;
                text-align: center;
                background: rgba(255, 255, 255, 0.2);
                font-weight: bold;
                color: white;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4CAF50, stop:1 #8BC34A);
                border-radius: 10px;
            }
        """)
        
        # Çıxış düyməsi
        exit_button = QPushButton("❌ İMTİNA (ESC)")
        exit_button.setFixedSize(150, 40)
        exit_button.setFont(QFont("Segoe UI", 10))
        exit_button.setStyleSheet("""
            QPushButton {
                background: rgba(244, 67, 54, 0.8);
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(244, 67, 54, 1);
            }
        """)
        exit_button.clicked.connect(self.reject)
        
        # Layout-a əlavə et
        main_layout.addWidget(title_label)
        
        # Barmaq izi ikonunu mərkəzləşdir
        icon_layout = QHBoxLayout()
        icon_layout.addStretch()
        icon_layout.addWidget(fingerprint_label)
        icon_layout.addStretch()
        main_layout.addLayout(icon_layout)
        
        main_layout.addWidget(self.status_label)
        main_layout.addWidget(self.progress_bar)
        
        # Çıxış düyməsini mərkəzləşdir
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(exit_button)
        button_layout.addStretch()
        main_layout.addLayout(button_layout)
        
        main_layout.addStretch()
        
    def set_gradient_background(self):
        """Gradient arxa fon təyin et"""
        palette = self.palette()
        gradient = QLinearGradient(0, 0, 0, 1)
        gradient.setCoordinateMode(QLinearGradient.ObjectBoundingMode)
        gradient.setColorAt(0, QColor(0, 188, 212))   # BioScript mavi
        gradient.setColorAt(1, QColor(0, 96, 139))    # Tünd BioScript mavi
        palette.setBrush(QPalette.Window, QBrush(gradient))
        self.setPalette(palette)
        
    def start_fake_scan(self):
        """Saxta barmaq izi oxuma prosesini başlat"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(50)  # Hər 50ms-də bir yenilə
        
    def update_progress(self):
        """Progress-i yenilə"""
        self.progress_value += 2
        self.progress_bar.setValue(self.progress_value)
        
        if self.progress_value <= 30:
            self.status_label.setText("Barmaq izi axtarılır...")
        elif self.progress_value <= 60:
            self.status_label.setText("Barmaq izi oxunur...")
        elif self.progress_value <= 90:
            self.status_label.setText("Məlumatlar yoxlanılır...")
        elif self.progress_value >= 100:
            self.timer.stop()
            self.status_label.setText("✅ Barmaq izi uğurla oxundu!")
            
            # 2 saniyə sonra dialog-u bağla
            QTimer.singleShot(2000, self.accept)
            
    def keyPressEvent(self, event):
        """ESC açarı ilə çıxış"""
        if event.key() == Qt.Key_Escape:
            self.reject()
        super().keyPressEvent(event)