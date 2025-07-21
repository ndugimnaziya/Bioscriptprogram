#!/usr/bin/env python3
"""
BioScript - Yalançı Barmaq İzi Oxuma Progress
Fake progress bar ilə barmaq izi simulasiyası
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QProgressBar, QFrame)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QMovie
from datetime import datetime

class FakeFingerprintProgressDialog(QDialog):
    """Yalançı barmaq izi oxuma progress dialoqu"""
    
    fingerprint_completed = pyqtSignal()  # Barmaq izi tamamlandı
    
    def __init__(self):
        super().__init__()
        self.progress_value = 0
        self.init_ui()
        self.start_fake_progress()
        
    def init_ui(self):
        """Tam ekran UI yaratma"""
        self.setWindowTitle("🔍 Barmaq İzi Oxunur - BioScript")
        
        # Tam ekran dialog
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.showFullScreen()
        self.setModal(True)
        
        # Ana tam ekran layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Tam ekran arxa fon
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #e3f2fd, stop:0.5 #f0f8ff, 
                                          stop:1 #e1f5fe);
            }
        """)
        
        # Mərkəz kontainer - tam ekran mərkəzləşdirmə
        center_widget = QFrame()
        center_layout = QVBoxLayout(center_widget)
        center_layout.setAlignment(Qt.AlignCenter)
        center_layout.setContentsMargins(50, 50, 50, 50)
        center_layout.setSpacing(0)
        
        # Ana çərçivə - kompakt ölçü
        main_frame = QFrame()
        main_frame.setFixedSize(600, 450)
        main_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #ffffff, stop:1 #f8f9fa);
                border: 4px solid #1e88e5;
                border-radius: 25px;
                padding: 25px;
                margin: auto;
            }
        """)
        frame_layout = QVBoxLayout(main_frame)
        frame_layout.setSpacing(15)
        frame_layout.setContentsMargins(20, 20, 20, 20)
        
        # Başlıq - daha böyük
        title = QLabel("🔍 Barmaq İzi Oxunur")
        title.setFont(QFont("Segoe UI", 22, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setFixedHeight(90)
        title.setStyleSheet("""
            color: #1565c0; 
            padding: 20px;
            background: #e3f2fd;
            border-radius: 15px;
            border: 2px solid #bbdefb;
            margin: 5px 0;
        """)
        
        # Barmaq izi animasiya ikonu - böyük
        fingerprint_icon = QLabel("👆")
        fingerprint_icon.setFont(QFont("Arial", 90))
        fingerprint_icon.setAlignment(Qt.AlignCenter)
        fingerprint_icon.setFixedHeight(140)
        fingerprint_icon.setStyleSheet("""
            padding: 25px;
            background: #f5f5f5;
            border-radius: 20px;
            border: 3px dashed #1565c0;
            margin: 8px 0;
        """)
        
        # Status mesajı - böyük
        self.status_label = QLabel("Barmaq izi oxuma başlanır...")
        self.status_label.setFont(QFont("Segoe UI", 15, QFont.Bold))
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setWordWrap(True)
        self.status_label.setFixedHeight(80)
        self.status_label.setStyleSheet("""
            color: #1565c0; 
            padding: 20px;
            background: #e8f5e8;
            border-radius: 12px;
            border: 2px solid #4caf50;
            margin: 8px 0;
        """)
        
        # Progress bar - böyük
        self.progress = QProgressBar()
        self.progress.setFixedHeight(50)
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 3px solid #1565c0;
                border-radius: 25px;
                text-align: center;
                font-weight: bold;
                background: white;
                font-size: 16px;
                color: #1565c0;
                margin: 8px 0;
                padding: 5px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #4caf50, stop: 1 #2e7d32);
                border-radius: 22px;
                margin: 3px;
            }
        """)
        
        # Layout-a əlavə et
        frame_layout.addWidget(title)
        frame_layout.addWidget(fingerprint_icon)
        frame_layout.addWidget(self.status_label)
        frame_layout.addWidget(self.progress)
        
        # Az boş yer əlavə et
        frame_layout.addStretch(0)
        
        # ESC açarı üçün çıxış düyməsi - alt hissədə
        exit_btn_layout = QHBoxLayout()
        exit_btn_layout.setContentsMargins(0, 15, 0, 0)
        exit_btn = QPushButton("ÇIXIŞ (ESC)")
        exit_btn.setFont(QFont("Segoe UI", 11))
        exit_btn.setFixedSize(110, 35)
        exit_btn.setStyleSheet("""
            QPushButton {
                background: #f44336;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #d32f2f;
            }
        """)
        exit_btn.clicked.connect(self.reject)
        exit_btn_layout.addStretch()
        exit_btn_layout.addWidget(exit_btn)
        
        frame_layout.addLayout(exit_btn_layout)
        
        # Mərkəz containerə əlavə et
        center_layout.addWidget(main_frame)
        
        # Ana layout-a əlavə et
        layout.addWidget(center_widget)
        
        # Timer yaratma
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        
        # ESC açarı üçün event filter
        self.installEventFilter(self)
        
    def eventFilter(self, obj, event):
        """ESC açarı ilə çıxış"""
        if event.type() == event.KeyPress and event.key() == Qt.Key_Escape:
            self.reject()
            return True
        return super().eventFilter(obj, event)
        
    def start_fake_progress(self):
        """Yalançı progress başlatma"""
        self.progress_value = 0
        self.timer.start(50)  # Hər 50ms-də yenilə
        
    def update_progress(self):
        """Progress yeniləmə"""
        self.progress_value += 1
        
        # Progress mərhələləri
        if self.progress_value <= 20:
            self.status_label.setText("Barmaq izi skaner hazırlanır...")
        elif self.progress_value <= 40:
            self.status_label.setText("Barmaq izi oxunur...")
        elif self.progress_value <= 60:
            self.status_label.setText("Məlumatlar təhlil edilir...")
        elif self.progress_value <= 80:
            self.status_label.setText("Verilənlər bazası ilə müqayisə edilir...")
        elif self.progress_value <= 95:
            self.status_label.setText("Pasiyent məlumatları tapılır...")
        elif self.progress_value >= 100:
            self.status_label.setText("✅ Barmaq izi uğurla oxunuldu!")
            self.status_label.setStyleSheet("""
                color: #2e7d32; 
                margin: 15px;
                padding: 12px;
                background: #e8f5e8;
                border-radius: 12px;
                border: 2px solid #4caf50;
                min-height: 50px;
            """)
            self.timer.stop()
            
            # 2 saniyə sonra dialoqu bağla və pasiyent listini aç
            QTimer.singleShot(2000, self.complete_scanning)
            return
            
        self.progress.setValue(self.progress_value)
        
    def complete_scanning(self):
        """Barmaq izi oxuma tamamlandı"""
        self.fingerprint_completed.emit()
        self.accept()