#!/usr/bin/env python3
"""
BioScript - Real AS608 Barmaq İzi Oxuyucu
Arduino AS608 sensor ilə birbaşa əlaqə
"""

import serial
import time
import threading
from database.db_manager import DatabaseManager

class RealFingerprintReader:
    """Real AS608 barmaq izi oxuyucu sistemi"""
    
    def __init__(self, port=None, baudrate=57600):
        self.baudrate = baudrate
        self.serial_conn = None
        self.is_connected = False
        self.db_manager = DatabaseManager()
        
        # Mövcud portları yoxla
        self.available_ports = self.detect_available_ports()
        self.port = port or self.auto_detect_port()
        
    def detect_available_ports(self):
        """Mövcud serial portları aşkar etmə"""
        import serial.tools.list_ports
        ports = []
        
        # Sistem portları
        for port in serial.tools.list_ports.comports():
            ports.append(port.device)
            
        # Ümumi Arduino portları
        common_ports = ['/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyACM0', '/dev/ttyACM1', 
                       'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8']
        
        for port in common_ports:
            if port not in ports:
                ports.append(port)
                
        return ports
    
    def auto_detect_port(self):
        """AS608 olan portu avtomatik tapmaq"""
        print("🔍 AS608 oxuyucu axtarılır...")
        
        for port in self.available_ports:
            try:
                print(f"Port yoxlanılır: {port}")
                test_conn = serial.Serial(port, self.baudrate, timeout=2)
                
                # AS608 test komandası göndər
                test_packet = b'\xEF\x01\xFF\xFF\xFF\xFF\x01\x00\x07\x13\x00\x00\x00\x00\x1B'
                test_conn.write(test_packet)
                
                # Cavab gözlə
                response = test_conn.read(12)
                test_conn.close()
                
                if len(response) >= 10 and response[0:2] == b'\xEF\x01':
                    print(f"✅ AS608 tapıldı: {port}")
                    return port
                    
            except Exception as e:
                continue
                
        print("❌ AS608 oxuyucu tapılmadı")
        print("⚠️ Arduino-nu bağlayın və AS608 kodunu yükləyin")
        return None
    
    def connect(self):
        """AS608 ilə real bağlantı qurma"""
        if not self.port:
            print("❌ Port tapılmadı - əvvəlcə Arduino bağlayın")
            return False
            
        try:
            print(f"🔗 {self.port} portuna bağlanır...")
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=3,
                write_timeout=3
            )
            
            time.sleep(2)  # Arduino restart gözləmə
            
            # Bağlantını test et
            if self.test_sensor():
                self.is_connected = True
                print(f"✅ AS608 uğurla bağlandı ({self.port})")
                return True
            else:
                self.serial_conn.close()
                print("❌ AS608 cavab vermir")
                return False
                
        except Exception as e:
            print(f"❌ Bağlantı xətası: {e}")
            self.is_connected = False
            return False
    
    def test_sensor(self):
        """AS608 sensorunu test etmə"""
        try:
            # VfyPwd komandası - sensor test
            test_cmd = b'\xEF\x01\xFF\xFF\xFF\xFF\x01\x00\x07\x13\x00\x00\x00\x00\x1B'
            self.serial_conn.write(test_cmd)
            
            response = self.serial_conn.read(12)
            
            if len(response) >= 10:
                if response[0:2] == b'\xEF\x01' and response[9] == 0x00:
                    print("✅ AS608 sensor aktiv")
                    return True
                    
            return False
            
        except Exception as e:
            print(f"Test xətası: {e}")
            return False
    
    def disconnect(self):
        """Bağlantını kəsmə"""
        if self.serial_conn and self.is_connected:
            self.serial_conn.close()
            self.is_connected = False
            print("🔌 AS608 bağlantısı kəsildi")
    
    def send_packet(self, command, data=[]):
        """AS608-ə paket göndərmə"""
        if not self.is_connected or not self.serial_conn:
            return None
            
        try:
            # Paket strukturu: Header + Address + Type + Length + Command + Data + Checksum
            packet = bytearray()
            packet.extend(b'\xEF\x01')  # Header
            packet.extend(b'\xFF\xFF\xFF\xFF')  # Address (default)
            packet.append(0x01)  # Command packet
            
            # Uzunluq hesabla
            data_length = len(data) + 3  # command(1) + checksum(2)
            packet.extend([(data_length >> 8) & 0xFF, data_length & 0xFF])
            
            # Komanda və data
            packet.append(command)
            packet.extend(data)
            
            # Checksum hesabla
            checksum = sum(packet[6:]) & 0xFFFF
            packet.extend([(checksum >> 8) & 0xFF, checksum & 0xFF])
            
            # Göndər
            self.serial_conn.write(packet)
            self.serial_conn.flush()
            
            return self.read_response()
            
        except Exception as e:
            print(f"Paket göndərmə xətası: {e}")
            return None
    
    def read_response(self):
        """AS608-dən cavab oxuma"""
        try:
            # Header axtarış
            while True:
                byte1 = self.serial_conn.read(1)
                if not byte1:
                    return None
                    
                if byte1 == b'\xEF':
                    byte2 = self.serial_conn.read(1)
                    if byte2 == b'\x01':
                        break
                        
            # Qalan header məlumatları
            address = self.serial_conn.read(4)  # Address
            packet_type = self.serial_conn.read(1)  # Packet type
            length_bytes = self.serial_conn.read(2)  # Length
            
            if len(length_bytes) < 2:
                return None
                
            length = (length_bytes[0] << 8) | length_bytes[1]
            
            # Payload oxu
            payload = self.serial_conn.read(length)
            
            if len(payload) >= 3:  # En azı confirmation code + checksum
                return payload
                
            return None
            
        except Exception as e:
            print(f"Cavab oxuma xətası: {e}")
            return None
    
    def capture_image(self):
        """Barmaq izi görüntüsü çəkmə"""
        print("📷 Barmağınızı sensora qoyun...")
        
        response = self.send_packet(0x01)  # GenImg command
        
        if response and response[0] == 0x00:
            print("✅ Görüntü çəkildi")
            return True
        elif response and response[0] == 0x02:
            print("❌ Barmaq tapılmadı")
        elif response and response[0] == 0x03:
            print("❌ Görüntü keyfiyyəti aşağı")
        else:
            print("❌ Görüntü çəkilə bilmədi")
            
        return False
    
    def img_to_tz(self, char_buffer):
        """Görüntünü template-ə çevirmə"""
        print("🔄 Barmaq izi analiz edilir...")
        
        response = self.send_packet(0x02, [char_buffer])  # Img2Tz command
        
        if response and response[0] == 0x00:
            print("✅ Template yaradıldı")
            return True
        elif response and response[0] == 0x06:
            print("❌ Görüntü çox qarışıq")
        elif response and response[0] == 0x07:
            print("❌ Xüsusiyyət nöqtələri kifayət deyil")
        else:
            print("❌ Template yaradıla bilmədi")
            
        return False
    
    def search_template(self, char_buffer=1, start_page=0, page_num=100):
        """Template axtarışı"""
        print("🔍 Bazada axtarılır...")
        
        data = [char_buffer, (start_page >> 8) & 0xFF, start_page & 0xFF, 
                (page_num >> 8) & 0xFF, page_num & 0xFF]
        response = self.send_packet(0x04, data)  # Search command
        
        if response and response[0] == 0x00:
            # Tapıldı
            page_id = (response[1] << 8) | response[2]
            match_score = (response[3] << 8) | response[4]
            print(f"✅ Barmaq izi tanındı! ID: {page_id}, Xal: {match_score}")
            return True, page_id, match_score
        elif response and response[0] == 0x09:
            print("❌ Barmaq izi tapılmadı")
        else:
            print("❌ Axtarış xətası")
            
        return False, None, None
    
    def verify_fingerprint(self):
        """Tam barmaq izi təsdiqləməsi"""
        if not self.is_connected:
            print("❌ AS608 bağlı deyil")
            return False, None
            
        try:
            # 1. Görüntü çək
            if not self.capture_image():
                return False, None
            
            # 2. Template yarat
            if not self.img_to_tz(1):
                return False, None
            
            # 3. Axtarış
            found, finger_id, score = self.search_template(1)
            
            if found and score > 50:  # Minimum uyğunluq
                print(f"🎉 Barmaq izi təsdiqləndi! Həkim ID: {finger_id}")
                return True, finger_id
            else:
                print("❌ Barmaq izi tanınmadı və ya uyğunluq aşağı")
                return False, None
                
        except Exception as e:
            print(f"❌ Təsdiqləmə xətası: {e}")
            return False, None
    
    def enroll_fingerprint(self, finger_id):
        """Yeni barmaq izi qeydiyyatı"""
        if not self.is_connected:
            print("❌ AS608 bağlı deyil")
            return False
            
        print(f"📝 Qeydiyyat başladı (ID: {finger_id})")
        
        try:
            # 1-ci çəkim
            print("1️⃣ Barmağınızı qoyun...")
            if not self.capture_image():
                return False
                
            if not self.img_to_tz(1):
                return False
            
            print("Barmağı çıxarın və bir az gözləyin...")
            time.sleep(2)
            
            # 2-ci çəkim
            print("2️⃣ Eyni barmağı yenidən qoyun...")
            if not self.capture_image():
                return False
                
            if not self.img_to_tz(2):
                return False
            
            # Template-ləri birləşdir
            response = self.send_packet(0x05)  # RegModel command
            
            if not response or response[0] != 0x00:
                print("❌ Template birləşdirmə xətası")
                return False
            
            # Bazaya saxla
            data = [0x01, (finger_id >> 8) & 0xFF, finger_id & 0xFF]
            response = self.send_packet(0x06, data)  # Store command
            
            if response and response[0] == 0x00:
                print(f"✅ Barmaq izi qeydiyyatı tamamlandı (ID: {finger_id})")
                return True
            else:
                print("❌ Saxlama xətası")
                return False
                
        except Exception as e:
            print(f"❌ Qeydiyyat xətası: {e}")
            return False
    
    def delete_fingerprint(self, finger_id):
        """Barmaq izi silmə"""
        data = [(finger_id >> 8) & 0xFF, finger_id & 0xFF, 0x00, 0x01]
        response = self.send_packet(0x0C, data)  # DeletChar command
        
        if response and response[0] == 0x00:
            print(f"✅ Barmaq izi silindi (ID: {finger_id})")
            return True
        else:
            print(f"❌ Barmaq izi silinə bilmədi (ID: {finger_id})")
            return False
    
    def get_template_count(self):
        """Saxlanmış template sayı"""
        response = self.send_packet(0x1D)  # TemplateNum command
        
        if response and response[0] == 0x00:
            count = (response[1] << 8) | response[2]
            print(f"📊 Bazada {count} barmaq izi var")
            return count
        
        return 0
    
    def find_doctor_by_fingerprint(self, finger_id):
        """Barmaq izi ilə həkim tapma"""
        try:
            # Həkim cədvəlində finger_id field-i olmalıdır
            query = "SELECT * FROM doctors WHERE fingerprint_id = %s"
            self.db_manager.cursor.execute(query, (finger_id,))
            doctor = self.db_manager.cursor.fetchone()
            
            if doctor:
                print(f"👨‍⚕️ Həkim tapıldı: {doctor['name']}")
                return doctor
            else:
                print("❌ Bu barmaq izi ilə həkim tapılmadı")
                return None
                
        except Exception as e:
            print(f"Həkim axtarış xətası: {e}")
            return None

# Test və debugging üçün
def test_fingerprint_reader():
    """AS608 test funksiyası"""
    reader = RealFingerprintReader()
    
    print("=== AS608 Barmaq İzi Oxuyucu Test ===")
    
    if reader.connect():
        count = reader.get_template_count()
        
        while True:
            print("\n1. Barmaq izi təsdiqləmə")
            print("2. Yeni barmaq izi qeydiyyatı")
            print("3. Template sayını göstər")
            print("4. Çıxış")
            
            choice = input("Seçiminiz: ")
            
            if choice == '1':
                success, finger_id = reader.verify_fingerprint()
                if success:
                    doctor = reader.find_doctor_by_fingerprint(finger_id)
                    
            elif choice == '2':
                finger_id = int(input("Yeni ID daxil edin: "))
                reader.enroll_fingerprint(finger_id)
                
            elif choice == '3':
                reader.get_template_count()
                
            elif choice == '4':
                break
    
    reader.disconnect()

if __name__ == "__main__":
    test_fingerprint_reader()