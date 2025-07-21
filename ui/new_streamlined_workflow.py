#!/usr/bin/env python3
"""
BioScript - Yeni Streamlined Workflow
Fake barmaq izi → Pasiyent seçimi → AI təhlil → Yeni resept
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QStackedWidget)
from PyQt5.QtCore import Qt, pyqtSignal

from .fake_fingerprint_progress import FakeFingerprintProgressDialog
from .patient_selection_dialog import PatientSelectionDialog
from .patient_history_ai_widget import PatientHistoryAIWidget

class NewStreamlinedWorkflow(QWidget):
    """Yeni streamlined workflow - tam proses"""
    
    workflow_completed = pyqtSignal()  # Workflow tamamlandı
    
    def __init__(self, db_manager, doctor_id):
        super().__init__()
        self.db_manager = db_manager
        self.doctor_id = doctor_id
        self.selected_patient = None
        
        self.init_ui()
        
    def init_ui(self):
        """UI yaratma"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Stacked widget workflow mərhələləri üçün
        self.stack = QStackedWidget()
        layout.addWidget(self.stack)
        
    def start_workflow(self):
        """Workflow-u başlat"""
        # 1. Fake barmaq izi oxuma
        self.start_fingerprint_scan()
        
    def start_fingerprint_scan(self):
        """Fake barmaq izi oxuma başlat"""
        fingerprint_dialog = FakeFingerprintProgressDialog()
        fingerprint_dialog.fingerprint_completed.connect(self.on_fingerprint_completed)
        fingerprint_dialog.exec_()
        
    def on_fingerprint_completed(self):
        """Barmaq izi oxuma tamamlandı, pasiyent seçiminə keç"""
        self.show_patient_selection()
        
    def show_patient_selection(self):
        """Pasiyent seçim dialoqu göstər"""
        patient_dialog = PatientSelectionDialog(self.db_manager)
        patient_dialog.patient_selected.connect(self.on_patient_selected)
        
        if patient_dialog.exec_() != patient_dialog.Accepted:
            # İstifadəçi ləğv etdi
            self.workflow_completed.emit()
            
    def on_patient_selected(self, patient_data):
        """Pasiyent seçildi, AI təhlil və resept yazma səhifəsinə keç"""
        self.selected_patient = patient_data
        
        # Pasiyent tarixçəsi və AI widget yaradıb stack-ə əlavə et
        history_widget = PatientHistoryAIWidget(
            self.db_manager, 
            patient_data, 
            self.doctor_id
        )
        history_widget.prescription_completed.connect(self.on_prescription_completed)
        
        # Stack-i təmizlə və yeni widget əlavə et
        while self.stack.count():
            child = self.stack.widget(0)
            self.stack.removeWidget(child)
            child.deleteLater()
            
        self.stack.addWidget(history_widget)
        self.stack.setCurrentWidget(history_widget)
        
    def on_prescription_completed(self):
        """Resept yazma tamamlandı"""
        self.workflow_completed.emit()