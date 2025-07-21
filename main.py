#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from ui.pharmacy_login import PharmacyLoginWindow

def main():
    # QT_QPA_PLATFORM=offscreen məhiti üçün
    if os.environ.get('QT_QPA_PLATFORM') == 'offscreen':
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'
    
    # Yüksek DPI dəstəyi - QApplication-dan əvvəl təyin edilməlidir
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    app.setApplicationName("BioScript Aptek Sistemi")
    app.setApplicationVersion("1.0")
    
    # Ana giriş pəncərəsi
    login_window = PharmacyLoginWindow()
    login_window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()