"""
BioScript - Verilənlər Bazası İdarəetmə Sistemi  
MySQL verilənlər bazası əlaqələri və əməliyyatlar
"""

import os
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import hashlib

class DatabaseManager:
    """Verilənlər bazası idarəetmə sinifi"""
    
    def __init__(self):
        self.connection = None
        self.cursor = None
        self.connect()
        self.create_tables()
    
    def connect(self):
        """Verilənlər bazasına bağlanma"""
        try:
            # MySQL bağlantı məlumatları
            self.connection = mysql.connector.connect(
                host='31.186.11.114',
                database='bio1criptshop_sayt',
                user='bio1criptshop_sayt',
                password='bioscriptsayt',
                charset='utf8mb4',
                collation='utf8mb4_general_ci'
            )
            
            self.cursor = self.connection.cursor(dictionary=True)
            print("MySQL verilənlər bazasına uğurla bağlanıldı")
            
        except Error as e:
            print(f"MySQL bağlantı xətası: {e}")
            raise
    
    def create_tables(self):
        """Cədvəllərin mövcudluğunu yoxlama - MySQL-də artıq yaradılıb"""
        try:
            # Cədvəllərin mövcudluğunu yoxla
            tables_to_check = ['doctors', 'patients', 'prescriptions', 'prescription_items', 'hospitals']
            
            for table in tables_to_check:
                self.cursor.execute(f"SHOW TABLES LIKE '{table}'")
                result = self.cursor.fetchone()
                if result:
                    print(f"✓ {table} cədvəli mövcuddur")
                else:
                    print(f"✗ {table} cədvəli tapılmadı")
            
            # Test məlumatları əlavə et (əgər yoxdursa)
            self.insert_test_data()
            
        except Error as e:
            print(f"Cədvəl yoxlama xətası: {e}")
            raise
    
    def insert_test_data(self):
        """Test məlumatları əlavə etmə"""
        try:
            # Test pasiyenti əlavə et (əgər yoxdursa)
            patient_check = """
            SELECT COUNT(*) as count FROM patients WHERE fin_code = %s
            """
            self.cursor.execute(patient_check, ('1234567',))
            result = self.cursor.fetchone()
            
            if result['count'] == 0:
                test_patient = """
                INSERT INTO patients (id, name, fin_code, birth_date, phone, address)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                self.cursor.execute(test_patient, (
                    'PAT001', 'Fatimə Əliyeva', '1234567', '1985-05-15', 
                    '+994551234567', 'Bakı şəhəri, Nəsimi rayonu'
                ))
                print("✓ Test pasiyenti əlavə edildi")
            
            self.connection.commit()
            
        except Error as e:
            print(f"Test məlumat əlavə etmə xətası: {e}")
            self.connection.rollback()
    
    def authenticate_doctor(self, username, password):
        """Həkim autentifikasiyası"""
        try:
            # MySQL schema-da password plain text saxlanılır (test üçün)
            query = """
            SELECT d.*, h.name as hospital_name 
            FROM doctors d
            LEFT JOIN hospitals h ON d.hospital_id = h.id
            WHERE d.username = %s AND d.password = %s AND d.is_active = 1
            """
            
            self.cursor.execute(query, (username, password))
            doctor = self.cursor.fetchone()
            
            if doctor:
                return doctor
            return None
            
        except Error as e:
            print(f"Həkim autentifikasiya xətası: {e}")
            return None
    
    def find_patient_by_fingerprint(self, finger_id):
        """Barmaq izi ilə pasiyent tapma"""
        try:
            query = """
            SELECT * FROM patients 
            WHERE fingerprint_id = %s AND is_active = 1
            """
            self.cursor.execute(query, (str(finger_id),))
            patient = self.cursor.fetchone()
            return patient
            
        except Error as e:
            print(f"Barmaq izi ilə pasiyent tapma xətası: {e}")
            return None
    
    def create_patient(self, patient_data):
        """Yeni pasiyent yaratma"""
        try:
            query = """
            INSERT INTO patients 
            (id, name, surname, birth_date, gender, phone, address, fingerprint_id, registered_at, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 1)
            """
            
            self.cursor.execute(query, (
                patient_data['id'],
                patient_data['name'],
                patient_data['surname'], 
                patient_data['birth_date'],
                patient_data['gender'],
                patient_data['phone'],
                patient_data['address'],
                patient_data['fingerprint_id'],
                patient_data['registered_at']
            ))
            
            self.connection.commit()
            print(f"Yeni pasiyent yaradıldı: {patient_data['id']}")
            return True
            
        except Error as e:
            print(f"Pasiyent yaratma xətası: {e}")
            self.connection.rollback()
            return False
    
    def search_patients(self, search_term):
        """Pasiyent axtarışı"""
        try:
            if not search_term.strip():
                # Boş axtarışda bütün pasiyentləri qaytarır
                query = "SELECT * FROM patients ORDER BY name LIMIT 50"
                self.cursor.execute(query)
            else:
                query = """
                SELECT * FROM patients 
                WHERE name LIKE %s OR fin_code LIKE %s OR phone LIKE %s OR id LIKE %s
                ORDER BY name
                """
                search_pattern = f"%{search_term}%"
                self.cursor.execute(query, (search_pattern, search_pattern, search_pattern, search_pattern))
            
            return self.cursor.fetchall()
            
        except Error as e:
            print(f"Pasiyent axtarış xətası: {e}")
            return []
    
    def get_patient_by_id(self, patient_id):
        """Pasiyenti ID ilə tapma"""
        try:
            query = "SELECT * FROM patients WHERE id = %s"
            self.cursor.execute(query, (patient_id,))
            
            patient = self.cursor.fetchone()
            return patient
            
        except Error as e:
            print(f"Pasiyent tapma xətası: {e}")
            return None
    
    def create_prescription(self, prescription_data):
        """Yeni resept yaratma"""
        try:
            # Həkimin hospital_id-ni al
            doctor_query = "SELECT hospital_id FROM doctors WHERE id = %s"
            self.cursor.execute(doctor_query, (prescription_data['doctor_id'],))
            doctor_result = self.cursor.fetchone()
            hospital_id = doctor_result['hospital_id'] if doctor_result else 1
            
            # Resept yaratma
            prescription_query = """
            INSERT INTO prescriptions (doctor_id, patient_id, hospital_id, complaint, diagnosis, status)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            
            self.cursor.execute(prescription_query, (
                prescription_data['doctor_id'],
                prescription_data['patient_id'],
                hospital_id,
                prescription_data['complaint'],
                prescription_data['diagnosis'],
                'active'
            ))
            
            prescription_id = self.cursor.lastrowid
            
            # Dərman elementlərini əlavə etmə
            for item in prescription_data['medications']:
                item_query = """
                INSERT INTO prescription_items 
                (prescription_id, name, dosage, instructions)
                VALUES (%s, %s, %s, %s)
                """
                
                instructions = f"Tezlik: {item.get('frequency', '')} | Müddət: {item.get('duration', '')} | {item.get('instructions', '')}"
                
                self.cursor.execute(item_query, (
                    prescription_id,
                    item['medication_name'],
                    item['dosage'],
                    instructions.strip()
                ))
            
            self.connection.commit()
            return prescription_id
            
        except Error as e:
            print(f"Resept yaratma xətası: {e}")
            self.connection.rollback()
            return None
    
    def get_patient_prescriptions(self, patient_id):
        """Pasiyentin reseptlərini tapma"""
        try:
            query = """
            SELECT p.*, d.name as doctor_name, d.surname as doctor_surname,
                   d.position as doctor_position, h.name as hospital_name
            FROM prescriptions p
            JOIN doctors d ON p.doctor_id = d.id
            LEFT JOIN hospitals h ON p.hospital_id = h.id
            WHERE p.patient_id = %s
            ORDER BY p.issued_at DESC
            """
            
            self.cursor.execute(query, (patient_id,))
            prescriptions = self.cursor.fetchall()
            
            # Hər resept üçün dərmanları əlavə et
            for prescription in prescriptions:
                items_query = """
                SELECT * FROM prescription_items 
                WHERE prescription_id = %s
                """
                self.cursor.execute(items_query, (prescription['id'],))
                prescription['medications'] = self.cursor.fetchall()
            
            return prescriptions
            
        except Error as e:
            print(f"Pasiyent reseptləri tapma xətası: {e}")
            return []
    
    def get_doctor_statistics(self, doctor_id, start_date=None, end_date=None):
        """Həkim statistikaları"""
        try:
            # Əsas statistikalar
            stats = {}
            
            # Ümumi resept sayı
            total_query = """
            SELECT COUNT(*) as total_prescriptions
            FROM prescriptions 
            WHERE doctor_id = %s
            """
            if start_date and end_date:
                total_query += " AND DATE(issued_at) BETWEEN %s AND %s"
                self.cursor.execute(total_query, (doctor_id, start_date, end_date))
            else:
                self.cursor.execute(total_query, (doctor_id,))
            
            result = self.cursor.fetchone()
            stats['total_prescriptions'] = result['total_prescriptions'] if result else 0
            
            # Unikal pasiyent sayı
            patients_query = """
            SELECT COUNT(DISTINCT patient_id) as unique_patients
            FROM prescriptions 
            WHERE doctor_id = %s
            """
            if start_date and end_date:
                patients_query += " AND DATE(issued_at) BETWEEN %s AND %s"
                self.cursor.execute(patients_query, (doctor_id, start_date, end_date))
            else:
                self.cursor.execute(patients_query, (doctor_id,))
            
            result = self.cursor.fetchone()
            stats['unique_patients'] = result['unique_patients'] if result else 0
            
            # Ən çox təyin olunan dərmanlar
            medications_query = """
            SELECT pi.name as medication_name, COUNT(*) as count
            FROM prescription_items pi
            JOIN prescriptions p ON pi.prescription_id = p.id
            WHERE p.doctor_id = %s
            """
            if start_date and end_date:
                medications_query += " AND DATE(p.issued_at) BETWEEN %s AND %s"
                medications_query += " GROUP BY pi.name ORDER BY count DESC LIMIT 10"
                self.cursor.execute(medications_query, (doctor_id, start_date, end_date))
            else:
                medications_query += " GROUP BY pi.name ORDER BY count DESC LIMIT 10"
                self.cursor.execute(medications_query, (doctor_id,))
            
            stats['top_medications'] = self.cursor.fetchall()
            
            return stats
            
        except Error as e:
            print(f"Statistika tapma xətası: {e}")
            return {'total_prescriptions': 0, 'unique_patients': 0, 'top_medications': []}
    
    def get_medications_list(self):
        """Dərmanlar siyahısını alma"""
        try:
            # Yaygın dərmanların sabit siyahısı
            common_medications = [
                {'name': 'Paracetamol', 'category': 'Ağrıkəsici'},
                {'name': 'Aspirin', 'category': 'Ağrıkəsici'},
                {'name': 'Ibuprofen', 'category': 'İltihabəleyhinə'},
                {'name': 'Amoxicillin', 'category': 'Antibiotik'},
                {'name': 'Ciprofloxacin', 'category': 'Antibiotik'},
                {'name': 'Metformin', 'category': 'Antidiabetik'},
                {'name': 'Atorvastatin', 'category': 'Statinlər'},
                {'name': 'Omeprazole', 'category': 'PPI'},
                {'name': 'Amlodipine', 'category': 'Antihipertensiv'},
                {'name': 'Losartan', 'category': 'ARB'},
                {'name': 'Vitamin D3', 'category': 'Vitamin'},
                {'name': 'Vitamin B12', 'category': 'Vitamin'},
                {'name': 'Folic Acid', 'category': 'Vitamin'},
                {'name': 'Iron Supplement', 'category': 'Mineral'},
                {'name': 'Dexamethasone', 'category': 'Kortikosteroid'}
            ]
            
            return common_medications
            
        except Error as e:
            print(f"Dərmanlar siyahısı xətası: {e}")
            return []
    
    def get_doctor_by_id(self, doctor_id):
        """Həkimi ID ilə tapma"""
        try:
            query = """
            SELECT d.*, h.name as hospital_name 
            FROM doctors d
            LEFT JOIN hospitals h ON d.hospital_id = h.id
            WHERE d.id = %s AND d.is_active = 1
            """
            self.cursor.execute(query, (doctor_id,))
            
            doctor = self.cursor.fetchone()
            return doctor
            
        except Error as e:
            print(f"Həkim tapma xətası: {e}")
            return None
    
    def close_connection(self):
        """Verilənlər bazası bağlantısını bağlama"""
        try:
            if self.cursor:
                self.cursor.close()
            if self.connection:
                self.connection.close()
        except Error as e:
            print(f"Bağlantı bağlama xətası: {e}")