#!/usr/bin/env python3
"""
BioScript - AS608 Barmaq İzi Oxuyucu
Arduino və AS608 sensor inteqrasiyası
"""

import serial
import time
import struct
from database.db_manager import DatabaseManager

class FingerprintReader:
    """AS608 barmaq izi oxuyucu sistemi"""
    
    def __init__(self, port='/dev/ttyUSB0', baudrate=57600):
        self.port = port
        self.baudrate = baudrate
        self.serial_conn = None
        self.db_manager = DatabaseManager()
        
        # AS608 komandaları
        self.COMMAND_PACKET = 0x01
        self.ACKPACKET = 0x07
        self.GETIMAGE = 0x01
        self.IMAGE2TZ = 0x02
        self.SEARCH = 0x04
        self.LOAD = 0x07
        self.STORE = 0x06
        
    def connect(self):
        """Arduino ilə bağlantı qurma"""
        try:
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=2
            )
            time.sleep(2)  # Arduino reset gözləmə
            print("✓ Arduino bağlantısı quruldu")
            return True
        except Exception as e:
            print(f"❌ Arduino bağlantı xətası: {e}")
            return False
    
    def disconnect(self):
        """Bağlantını kəsmə"""
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
            print("✓ Arduino bağlantısı kəsildi")
    
    def send_command(self, command, data=[]):
        """AS608-ə komanda göndərmə"""
        if not self.serial_conn or not self.serial_conn.is_open:
            return None
            
        # Paket formatı: Header + Address + Packet Type + Length + Command + Data + Checksum
        packet = [0xEF, 0x01]  # Header
        packet.extend([0xFF, 0xFF, 0xFF, 0xFF])  # Address
        packet.append(self.COMMAND_PACKET)  # Packet type
        
        length = len(data) + 3  # Command + checksum
        packet.extend([0x00, length])
        packet.append(command)
        packet.extend(data)
        
        # Checksum hesablama
        checksum = sum(packet[6:]) & 0xFFFF
        packet.extend([checksum >> 8, checksum & 0xFF])
        
        try:
            self.serial_conn.write(bytes(packet))
            return self.read_response()
        except Exception as e:
            print(f"Komanda göndərmə xətası: {e}")
            return None
    
    def read_response(self):
        """AS608-dən cavab oxuma"""
        try:
            # Header gözləmə
            while True:
                data = self.serial_conn.read(2)
                if len(data) == 2 and data == b'\xEF\x01':
                    break
                    
            # Qalan paketi oxuma
            address = self.serial_conn.read(4)  # Address
            packet_type = self.serial_conn.read(1)[0]  # Packet type
            length_bytes = self.serial_conn.read(2)  # Length
            length = (length_bytes[0] << 8) | length_bytes[1]
            
            payload = self.serial_conn.read(length)
            
            if len(payload) >= 1:
                return payload[0]  # Confirmation code
            return None
            
        except Exception as e:
            print(f"Cavab oxuma xətası: {e}")
            return None
    
    def capture_fingerprint(self):
        """Barmaq izi çəkmə"""
        print("🔍 Barmağınızı sensora qoyun...")
        
        # Şəkil çəkmə
        result = self.send_command(self.GETIMAGE)
        if result != 0x00:
            return None, "Barmaq izi oxuna bilmədi"
        
        # Şəkli template-ə çevirmə
        result = self.send_command(self.IMAGE2TZ, [1])
        if result != 0x00:
            return None, "Template yaradıla bilmədi"
        
        # Bazada axtarış
        result = self.send_command(self.SEARCH, [1, 0x00, 0x00, 0x00, 100])
        
        if result == 0x00:
            # Tapıldı - finger ID və confidence score alınmalı
            # Simulasiya üçün random ID qaytarırıq
            import random
            finger_id = random.randint(1, 100)
            return finger_id, "Barmaq izi tanındı"
        else:
            return None, "Barmaq izi tanınmadı"
    
    def find_patient_by_fingerprint(self, finger_id):
        """Barmaq izi ID-sinə görə pasiyent tapma"""
        try:
            # Burada finger_id ilə pasiyent axtarışı
            # Hal-hazırda simulasiya üçün test pasiyenti qaytarırıq
            query = "SELECT * FROM patients WHERE id = 'PAT001'"
            self.db_manager.cursor.execute(query)
            patient = self.db_manager.cursor.fetchone()
            return patient
        except Exception as e:
            print(f"Pasiyent axtarış xətası: {e}")
            return None
    
    def register_fingerprint(self, patient_id, finger_position=1):
        """Yeni barmaq izi qeydiyyatı"""
        print(f"📝 {patient_id} üçün barmaq izi qeydiyyatı...")
        
        # İki dəfə barmaq izi çəkmə
        for i in range(2):
            print(f"Barmağınızı {i+1}. dəfə sensora qoyun...")
            
            result = self.send_command(self.GETIMAGE)
            if result != 0x00:
                return False, f"{i+1}. çəkim uğursuz"
            
            result = self.send_command(self.IMAGE2TZ, [i+1])
            if result != 0x00:
                return False, f"{i+1}. template yaradıla bilmədi"
        
        # Template-ləri birləşdirmə və saxlama
        # Bu simulasiyadır - həqiqi implementasiya daha mürəkkəbdir
        finger_id = hash(patient_id) % 1000  # Simulasiya ID
        
        print(f"✓ Barmaq izi qeydiyyatı tamamlandı (ID: {finger_id})")
        return True, finger_id

# Test simulasiyası üçün
class FingerprintSimulator(FingerprintReader):
    """Test üçün barmaq izi simulatoru"""
    
    def connect(self):
        print("🔧 Simulator rejimi - Arduino bağlantısı simulasiya edilir")
        return True
    
    def capture_fingerprint(self):
        print("🔍 Barmaq izi simulasiyası...")
        time.sleep(2)  # Realistik gözləmə
        
        # Test üçün əvvəlcədən qeydiyyatlı finger ID
        import random
        if random.choice([True, False]):  # 50% şans
            return 1, "Test barmaq izi tanındı"
        else:
            return None, "Barmaq izi tanınmadı"
    
    def find_patient_by_fingerprint(self, finger_id):
        # Test pasiyenti qaytarma
        return {
            'id': 'PAT001',
            'name': 'Fatimə Əliyeva',
            'fin_code': '1234567',
            'birth_date': '1985-05-15',
            'phone': '+994551234567'
        }