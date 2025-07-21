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
        """UI yaratma"""
        self.setWindowTitle("🔍 Barmaq İzi Oxunur - BioScript")
        self.setFixedSize(500, 350)
        self.setModal(True)
        
        # Pəncərəni mərkəzə yerləşdir
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(30)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Ana çərçivə
        main_frame = QFrame()
        main_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #ffffff, stop:1 #f8f9fa);
                border: 3px solid #1e88e5;
                border-radius: 20px;
                padding: 20px;
            }
        """)
        frame_layout = QVBoxLayout(main_frame)
        frame_layout.setSpacing(25)
        
        # Başlıq
        title = QLabel("🔍 Barmaq İzi Oxunur")
        title.setFont(QFont("Segoe UI", 22, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            color: #1565c0; 
            margin-bottom: 10px;
            padding: 15px;
            background: #e3f2fd;
            border-radius: 15px;
        """)
        
        # Barmaq izi animasiya ikonu
        fingerprint_icon = QLabel("👆")
        fingerprint_icon.setFont(QFont("Arial", 80))
        fingerprint_icon.setAlignment(Qt.AlignCenter)
        fingerprint_icon.setStyleSheet("""
            margin: 20px;
            padding: 25px;
            background: #f5f5f5;
            border-radius: 20px;
            border: 3px dashed #1565c0;
        """)
        
        # Status mesajı
        self.status_label = QLabel("Barmaq izi oxuma başlanır...")
        self.status_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet("""
            color: #1565c0; 
            margin: 15px;
            padding: 12px;
            background: #e8f5e8;
            border-radius: 12px;
            border: 2px solid #4caf50;
            min-height: 50px;
        """)
        
        # Progress bar
        self.progress = QProgressBar()
        self.progress.setFixedHeight(35)
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 3px solid #1565c0;
                border-radius: 18px;
                text-align: center;
                font-weight: bold;
                background: white;
                font-size: 14px;
                color: #1565c0;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #4caf50, stop: 1 #2e7d32);
                border-radius: 15px;
                margin: 3px;
            }
        """)
        
        # Layout-a əlavə et
        frame_layout.addWidget(title)
        frame_layout.addWidget(fingerprint_icon)
        frame_layout.addWidget(self.status_label)
        frame_layout.addWidget(self.progress)
        
        layout.addWidget(main_frame)
        
        # Timer yaratma
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        
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