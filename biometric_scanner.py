"""
BioScript - AS608 Barmaq İzi Skaneri
AS608 barmaq izi modulundan template çıxarma və server-side tanıma
"""

import serial
import time
import base64
import struct
from PyQt5.QtCore import QThread, pyqtSignal, QObject
import requests
import json

class AS608Scanner(QThread):
    """AS608 barmaq izi skaneri thread sinifi"""
    
    # Siqnallar
    scan_completed = pyqtSignal(str)  # Template base64
    scan_failed = pyqtSignal(str)     # Xəta mesajı
    scan_progress = pyqtSignal(str)   # Proses vəziyyəti
    
    def __init__(self, port="/dev/ttyUSB0", baudrate=57600):
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.serial_conn = None
        self.is_scanning = False
        
        # AS608 komanda kodları
        self.COMMAND_PACKET = 0x01
        self.DATA_PACKET = 0x02
        self.ACK_PACKET = 0x07
        self.END_PACKET = 0x08
        
        # AS608 əmr kodları
        self.CMD_GENCHAR = 0x02      # Barmaq izi xarakteristikası yaratma
        self.CMD_MATCH = 0x03        # İki template müqayisəsi
        self.CMD_SEARCH = 0x04       # Template axtarışı
        self.CMD_REGMODEL = 0x05     # Template yaratma
        self.CMD_STORE = 0x06        # Template yadda saxlama
        self.CMD_LOAD = 0x07         # Template yükləmə
        self.CMD_UPCHAR = 0x08       # Template yükləmə (kompyuterə)
        self.CMD_DOWNCHAR = 0x09     # Template endirmə (sensordan)
        self.CMD_IMGTOTZ = 0x12      # Şəkli TZ formatına çevirmə
        self.CMD_TZTOCHAR = 0x13     # TZ-ni xarakteristikaya çevirmə
        
    def connect_sensor(self):
        """AS608 sensoruna bağlanma"""
        try:
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=2
            )
            time.sleep(2)  # Sensor hazırlanması üçün gözləmə
            return True
        except Exception as e:
            self.scan_failed.emit(f"Sensor bağlantısı xətası: {str(e)}")
            return False
    
    def disconnect_sensor(self):
        """Sensor bağlantısını kəsmə"""
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
    
    def calculate_checksum(self, data):
        """Checksum hesablama"""
        return sum(data) & 0xFFFF
    
    def create_packet(self, command, data=None):
        """AS608 paketi yaratma"""
        if data is None:
            data = []
        
        # Paket header
        header = [0xEF, 0x01]  # Header
        address = [0xFF, 0xFF, 0xFF, 0xFF]  # Default address
        packet_type = [self.COMMAND_PACKET]
        length = [0x00, len(data) + 3]  # Command + data + checksum
        
        packet = header + address + packet_type + length + [command] + data
        
        # Checksum əlavə et
        checksum = self.calculate_checksum(packet_type + length + [command] + data)
        packet.extend([checksum >> 8, checksum & 0xFF])
        
        return bytes(packet)
    
    def send_command(self, command, data=None):
        """Komanda göndərmə"""
        if not self.serial_conn or not self.serial_conn.is_open:
            return None
        
        packet = self.create_packet(command, data)
        self.serial_conn.write(packet)
        
        # Cavab gözləmə
        time.sleep(0.5)
        if self.serial_conn.in_waiting > 0:
            response = self.serial_conn.read(self.serial_conn.in_waiting)
            return response
        
        return None
    
    def capture_fingerprint(self):
        """Barmaq izi şəklini çəkmə"""
        try:
            self.scan_progress.emit("Barmaq izinizi sensora qoyun...")
            
            # GenImg komandası - şəkil çəkmə
            response = self.send_command(0x01)  # GenImg
            if not response or len(response) < 12:
                raise Exception("Şəkil çəkilmədi")
            
            confirmation_code = response[9]
            if confirmation_code != 0x00:
                raise Exception(f"Şəkil çəkmə xətası: {confirmation_code}")
            
            self.scan_progress.emit("Şəkil çəkildi, xarakteristika yaradılır...")
            
            # Img2Tz komandası - şəkli template-ə çevirmə
            response = self.send_command(self.CMD_IMGTOTZ, [0x01])  # CharBuffer1-ə yaz
            if not response or len(response) < 12:
                raise Exception("Template yaradılmadı")
            
            confirmation_code = response[9]
            if confirmation_code != 0x00:
                raise Exception(f"Template yaratma xətası: {confirmation_code}")
            
            self.scan_progress.emit("Template yaradıldı, yüklənir...")
            
            # UpChar komandası - template-i yükləmə
            response = self.send_command(self.CMD_UPCHAR, [0x01])  # CharBuffer1-dən yüklə
            if not response or len(response) < 20:
                raise Exception("Template yüklənmədi")
            
            confirmation_code = response[9]
            if confirmation_code != 0x00:
                raise Exception(f"Template yükləmə xətası: {confirmation_code}")
            
            # Template məlumatlarını çıxarma
            template_data = response[10:-2]  # Checksum-u çıxar
            template_base64 = base64.b64encode(template_data).decode('utf-8')
            
            return template_base64
            
        except Exception as e:
            raise Exception(f"Barmaq izi çəkilməsində xəta: {str(e)}")
    
    def run(self):
        """Thread işə salınması"""
        self.is_scanning = True
        
        try:
            if not self.connect_sensor():
                return
            
            self.scan_progress.emit("Sensor hazırdır...")
            
            # Barmaq izi çəkmə
            template = self.capture_fingerprint()
            
            self.scan_progress.emit("Barmaq izi uğurla oxundu!")
            self.scan_completed.emit(template)
            
        except Exception as e:
            self.scan_failed.emit(str(e))
        
        finally:
            self.disconnect_sensor()
            self.is_scanning = False
    
    def stop_scanning(self):
        """Skanları dayandırma"""
        self.is_scanning = False
        self.terminate()


class BiometricMatcher(QObject):
    """Server-side biometrik tanıma sinifi"""
    
    match_completed = pyqtSignal(dict)  # Tanıma nəticəsi
    match_failed = pyqtSignal(str)      # Xəta mesajı
    
    def __init__(self, server_url="http://localhost:8080"):
        super().__init__()
        self.server_url = server_url
    
    def match_fingerprint(self, template_base64, threshold=80):
        """
        Barmaq izi template-ini server-də mövcud template-lərlə müqayisə etmə
        Əsl sistemdə NBIS və ya VeriFinger SDK istifadə edilməlidir
        """
        try:
            # Server API-na sorğu göndərmə
            payload = {
                "template": template_base64,
                "threshold": threshold,
                "action": "match"
            }
            
            # Bu sadələşdirilmiş versiyada local matching simulyasiyası
            # Əsl sistemdə server-side biometric SDK istifadə edilməlidir
            
            # Mock response (test üçün)
            # Əsl sistemdə bu server-dən gələcək
            mock_response = {
                "success": False,  # Test üçün hər dəfə yeni pasiyent kimi qəbul edirik
                "patient_id": None,
                "confidence": 0
            }
            
            if mock_response["success"]:
                result = {
                    "found": True,
                    "patient_id": mock_response["patient_id"],
                    "confidence": mock_response["confidence"]
                }
            else:
                result = {
                    "found": False,
                    "patient_id": None,
                    "confidence": 0
                }
            
            self.match_completed.emit(result)
            return result
            
        except Exception as e:
            error_msg = f"Biometrik tanıma xətası: {str(e)}"
            self.match_failed.emit(error_msg)
            return None


# Mock AS608 Scanner (real hardware yoxdursa test üçün)
class MockAS608Scanner(QThread):
    """Test üçün mock AS608 skaneri"""
    
    scan_completed = pyqtSignal(str)
    scan_failed = pyqtSignal(str)
    scan_progress = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.is_scanning = False
    
    def run(self):
        """Mock skan prosesi"""
        self.is_scanning = True
        
        try:
            self.scan_progress.emit("Mock sensor hazırdır...")
            time.sleep(1)
            
            self.scan_progress.emit("Barmaq izinizi sensora qoyun...")
            time.sleep(2)
            
            self.scan_progress.emit("Şəkil çəkildi, xarakteristika yaradılır...")
            time.sleep(1)
            
            self.scan_progress.emit("Template yaradıldı, yüklənir...")
            time.sleep(1)
            
            # Mock template yaratma
            import random
            mock_template = base64.b64encode(
                bytes([random.randint(0, 255) for _ in range(256)])
            ).decode('utf-8')
            
            self.scan_progress.emit("Barmaq izi uğurla oxundu!")
            self.scan_completed.emit(mock_template)
            
        except Exception as e:
            self.scan_failed.emit(str(e))
        
        finally:
            self.is_scanning = False
    
    def stop_scanning(self):
        """Mock skanı dayandırma"""
        self.is_scanning = False
        self.terminate()