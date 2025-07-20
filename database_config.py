"""
BioScript - Verilənlər Bazası Konfiqurasiyası
MySQL verilənlər bazası bağlantısı və əsas əməliyyatlar
"""

import mysql.connector
from mysql.connector import Error
import base64
import hashlib
from datetime import datetime
import json

class DatabaseManager:
    def __init__(self):
        self.host = "31.186.11.114"
        self.user = "bio1criptshop_sayt"
        self.password = "bioscriptsayt"
        self.database = "bio1criptshop_sayt"
        self.connection = None
        self.cursor = None
    
    def connect(self):
        """Verilənlər bazasına bağlantı"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                autocommit=True
            )
            self.cursor = self.connection.cursor(dictionary=True)
            return True
        except Error as e:
            print(f"Verilənlər bazası bağlantı xətası: {e}")
            return False
    
    def disconnect(self):
        """Bağlantını bağla"""
        if self.cursor:
            self.cursor.close()
        if self.connection and self.connection.is_connected():
            self.connection.close()
    
    def authenticate_doctor(self, username, password):
        """Həkim autentifikasiyası"""
        try:
            # Parolun hash-i
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            query = """
            SELECT id, username, name, specialty, phone 
            FROM doctors 
            WHERE username = %s AND password_hash = %s AND status = 'active'
            """
            
            self.cursor.execute(query, (username, password_hash))
            doctor = self.cursor.fetchone()
            
            if doctor:
                # Son giriş vaxtını yenilə
                update_query = "UPDATE doctors SET last_login = NOW() WHERE id = %s"
                self.cursor.execute(update_query, (doctor['id'],))
                
            return doctor
            
        except Error as e:
            print(f"Autentifikasiya xətası: {e}")
            return None
    
    def get_patient_by_fingerprint(self, fingerprint_template):
        """Barmaq izi ilə pasiyent tapma"""
        try:
            # Əsl sistemdə burada biometrik tanıma SDK-sı istifadə edilməlidir
            # Bu sadələşdirilmiş versiyada template base64 müqayisəsi edilir
            
            query = """
            SELECT id, name, surname, birth_date, phone, address
            FROM patients 
            WHERE fingerprint_template = %s AND status = 'active'
            """
            
            self.cursor.execute(query, (fingerprint_template,))
            patient = self.cursor.fetchone()
            
            return patient
            
        except Error as e:
            print(f"Pasiyent axtarışında xəta: {e}")
            return None
    
    def register_new_patient(self, patient_data, fingerprint_template):
        """Yeni pasiyent qeydiyyatı"""
        try:
            query = """
            INSERT INTO patients (name, surname, birth_date, phone, address, 
                                fingerprint_template, registration_date, status)
            VALUES (%s, %s, %s, %s, %s, %s, NOW(), 'active')
            """
            
            values = (
                patient_data['name'],
                patient_data['surname'],
                patient_data['birth_date'],
                patient_data['phone'],
                patient_data['address'],
                fingerprint_template
            )
            
            self.cursor.execute(query, values)
            patient_id = self.cursor.lastrowid
            
            return patient_id
            
        except Error as e:
            print(f"Pasiyent qeydiyyatında xəta: {e}")
            return None
    
    def create_prescription(self, doctor_id, patient_id, complaint, diagnosis):
        """Yeni resept yaratma"""
        try:
            query = """
            INSERT INTO prescriptions (doctor_id, patient_id, hospital_id, 
                                     complaint, diagnosis, prescription_date, status)
            VALUES (%s, %s, 1, %s, %s, NOW(), 'active')
            """
            
            values = (doctor_id, patient_id, complaint, diagnosis)
            self.cursor.execute(query, values)
            prescription_id = self.cursor.lastrowid
            
            return prescription_id
            
        except Error as e:
            print(f"Resept yaradılmasında xəta: {e}")
            return None
    
    def add_prescription_items(self, prescription_id, medications):
        """Reseptə dərmanlar əlavə etmə"""
        try:
            query = """
            INSERT INTO prescription_items (prescription_id, medication_name, 
                                          dosage, instructions, quantity)
            VALUES (%s, %s, %s, %s, %s)
            """
            
            for med in medications:
                values = (
                    prescription_id,
                    med['name'],
                    med['dosage'],
                    med['instructions'],
                    med.get('quantity', 1)
                )
                self.cursor.execute(query, values)
            
            return True
            
        except Error as e:
            print(f"Dərman əlavə edilməsində xəta: {e}")
            return False
    
    def get_patient_history(self, patient_id):
        """Pasiyentin resept tarixçəsi"""
        try:
            query = """
            SELECT p.id, p.complaint, p.diagnosis, p.prescription_date,
                   d.name as doctor_name, d.specialty,
                   pi.medication_name, pi.dosage, pi.instructions
            FROM prescriptions p
            JOIN doctors d ON p.doctor_id = d.id
            LEFT JOIN prescription_items pi ON p.id = pi.prescription_id
            WHERE p.patient_id = %s AND p.status = 'active'
            ORDER BY p.prescription_date DESC
            """
            
            self.cursor.execute(query, (patient_id,))
            history = self.cursor.fetchall()
            
            return history
            
        except Error as e:
            print(f"Pasiyent tarixçəsi alınmasında xəta: {e}")
            return []
    
    def get_doctor_statistics(self, doctor_id, period='month'):
        """Həkim statistikaları"""
        try:
            if period == 'day':
                date_condition = "DATE(prescription_date) = CURDATE()"
            elif period == 'month':
                date_condition = "MONTH(prescription_date) = MONTH(CURDATE()) AND YEAR(prescription_date) = YEAR(CURDATE())"
            else:
                date_condition = "YEAR(prescription_date) = YEAR(CURDATE())"
            
            query = f"""
            SELECT 
                COUNT(*) as total_prescriptions,
                COUNT(DISTINCT patient_id) as unique_patients,
                DATE(prescription_date) as date
            FROM prescriptions 
            WHERE doctor_id = %s AND {date_condition}
            GROUP BY DATE(prescription_date)
            ORDER BY date DESC
            """
            
            self.cursor.execute(query, (doctor_id,))
            stats = self.cursor.fetchall()
            
            return stats
            
        except Error as e:
            print(f"Statistika alınmasında xəta: {e}")
            return []
    
    def setup_database(self):
        """Verilənlər bazası cədvəllərini yaratma (ilk dəfə işə salınma üçün)"""
        try:
            # Həkimlər cədvəli
            doctors_table = """
            CREATE TABLE IF NOT EXISTS doctors (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password_hash VARCHAR(64) NOT NULL,
                name VARCHAR(100) NOT NULL,
                surname VARCHAR(100) NOT NULL,
                specialty VARCHAR(100),
                phone VARCHAR(20),
                email VARCHAR(100),
                registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP NULL,
                status ENUM('active', 'inactive') DEFAULT 'active'
            )
            """
            
            # Pasiyentlər cədvəli
            patients_table = """
            CREATE TABLE IF NOT EXISTS patients (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                surname VARCHAR(100) NOT NULL,
                birth_date DATE,
                phone VARCHAR(20),
                address TEXT,
                fingerprint_template LONGBLOB,
                registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status ENUM('active', 'inactive') DEFAULT 'active'
            )
            """
            
            # Reseptlər cədvəli
            prescriptions_table = """
            CREATE TABLE IF NOT EXISTS prescriptions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                doctor_id INT NOT NULL,
                patient_id INT NOT NULL,
                hospital_id INT DEFAULT 1,
                complaint TEXT,
                diagnosis TEXT,
                prescription_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status ENUM('active', 'completed', 'cancelled') DEFAULT 'active',
                FOREIGN KEY (doctor_id) REFERENCES doctors(id),
                FOREIGN KEY (patient_id) REFERENCES patients(id)
            )
            """
            
            # Dərman detalları cədvəli
            prescription_items_table = """
            CREATE TABLE IF NOT EXISTS prescription_items (
                id INT AUTO_INCREMENT PRIMARY KEY,
                prescription_id INT NOT NULL,
                medication_name VARCHAR(200) NOT NULL,
                dosage VARCHAR(100) NOT NULL,
                instructions TEXT,
                quantity INT DEFAULT 1,
                FOREIGN KEY (prescription_id) REFERENCES prescriptions(id)
            )
            """
            
            tables = [doctors_table, patients_table, prescriptions_table, prescription_items_table]
            
            for table_sql in tables:
                self.cursor.execute(table_sql)
            
            # Test həkim əlavə et
            test_doctor = """
            INSERT IGNORE INTO doctors (username, password_hash, name, surname, specialty, phone)
            VALUES ('hekim1', SHA2('123456', 256), 'Dr. Əli', 'Məmmədov', 'Ümumi Təbabət', '+994501234567')
            """
            self.cursor.execute(test_doctor)
            
            return True
            
        except Error as e:
            print(f"Verilənlər bazası qurulmasında xəta: {e}")
            return False