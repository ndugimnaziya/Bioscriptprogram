"""
BioScript - Verilənlər Bazası İdarəetmə Sistemi
PostgreSQL verilənlər bazası əlaqələri və əməliyyatlar
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
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
            # Replit PostgreSQL bağlantı məlumatları
            database_url = os.getenv('DATABASE_URL')
            if database_url:
                self.connection = psycopg2.connect(database_url)
            else:
                # Local test üçün
                self.connection = psycopg2.connect(
                    host=os.getenv('PGHOST', 'localhost'),
                    database=os.getenv('PGDATABASE', 'bioscript'),
                    user=os.getenv('PGUSER', 'postgres'),
                    password=os.getenv('PGPASSWORD', ''),
                    port=os.getenv('PGPORT', '5432')
                )
            
            self.cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            print("Verilənlər bazasına uğurla bağlanıldı")
            
        except Exception as e:
            print(f"Verilənlər bazası bağlantı xətası: {e}")
            raise
    
    def create_tables(self):
        """Verilənlər bazası cədvəllərini yaratma"""
        try:
            # Həkimlər cədvəli
            doctors_table = """
            CREATE TABLE IF NOT EXISTS doctors (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password_hash VARCHAR(64) NOT NULL,
                name VARCHAR(100) NOT NULL,
                surname VARCHAR(100) NOT NULL,
                specialty VARCHAR(100),
                phone VARCHAR(20),
                email VARCHAR(100),
                license_number VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE
            )
            """
            
            # Pasiyentlər cədvəli
            patients_table = """
            CREATE TABLE IF NOT EXISTS patients (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                surname VARCHAR(100) NOT NULL,
                birth_date DATE,
                gender VARCHAR(10),
                phone VARCHAR(20),
                address TEXT,
                id_number VARCHAR(20) UNIQUE,
                blood_type VARCHAR(5),
                allergies TEXT,
                chronic_diseases TEXT,
                emergency_contact VARCHAR(20),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            
            # Reseptlər cədvəli
            prescriptions_table = """
            CREATE TABLE IF NOT EXISTS prescriptions (
                id SERIAL PRIMARY KEY,
                doctor_id INTEGER NOT NULL REFERENCES doctors(id),
                patient_id INTEGER NOT NULL REFERENCES patients(id),
                complaint TEXT,
                diagnosis TEXT,
                notes TEXT,
                prescription_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status VARCHAR(20) DEFAULT 'active'
            )
            """
            
            # Dərman detalları cədvəli
            prescription_items_table = """
            CREATE TABLE IF NOT EXISTS prescription_items (
                id SERIAL PRIMARY KEY,
                prescription_id INTEGER NOT NULL REFERENCES prescriptions(id),
                medication_name VARCHAR(200) NOT NULL,
                dosage VARCHAR(100) NOT NULL,
                frequency VARCHAR(100) NOT NULL,
                duration VARCHAR(50) NOT NULL,
                instructions TEXT,
                quantity INTEGER DEFAULT 1
            )
            """
            
            # Dərmanlar lüğəti
            medications_table = """
            CREATE TABLE IF NOT EXISTS medications (
                id SERIAL PRIMARY KEY,
                name VARCHAR(200) NOT NULL,
                category VARCHAR(100),
                manufacturer VARCHAR(100),
                common_dosages TEXT,
                contraindications TEXT,
                side_effects TEXT,
                active_ingredient VARCHAR(200)
            )
            """
            
            tables = [
                doctors_table, 
                patients_table, 
                prescriptions_table, 
                prescription_items_table,
                medications_table
            ]
            
            for table_sql in tables:
                self.cursor.execute(table_sql)
            
            self.connection.commit()
            
            # İlkin məlumatları əlavə et
            self.insert_initial_data()
            
        except Exception as e:
            print(f"Cədvəl yaratma xətası: {e}")
            self.connection.rollback()
            raise
    
    def insert_initial_data(self):
        """İlkin test məlumatlarını əlavə etmə"""
        try:
            # Test həkimi
            test_doctor_check = """
            SELECT COUNT(*) FROM doctors WHERE username = %s
            """
            self.cursor.execute(test_doctor_check, ('hekim1',))
            
            if self.cursor.fetchone()['count'] == 0:
                password_hash = hashlib.sha256('123456'.encode()).hexdigest()
                test_doctor = """
                INSERT INTO doctors (username, password_hash, name, surname, specialty, phone, email)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                self.cursor.execute(test_doctor, (
                    'hekim1', password_hash, 'Əli', 'Məmmədov', 
                    'Ümumi Təbabət', '+994501234567', 'ali@bioscript.az'
                ))
            
            # Test pasienti
            test_patient_check = """
            SELECT COUNT(*) FROM patients WHERE id_number = %s
            """
            self.cursor.execute(test_patient_check, ('1234567890',))
            
            if self.cursor.fetchone()['count'] == 0:
                test_patient = """
                INSERT INTO patients (name, surname, birth_date, gender, phone, id_number, blood_type)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                self.cursor.execute(test_patient, (
                    'Fatimə', 'Əliyeva', '1985-05-15', 'Qadın', 
                    '+994551234567', '1234567890', 'A+'
                ))
            
            # Ümumi dərmanlar
            common_medications = [
                ('Paracetamol', 'Ağrıkəsici', 'Bayer', '500mg, 1000mg', 'Qaraciyər xəstəliyi', 'Mədə ağrısı', 'Acetaminophen'),
                ('Aspirin', 'Ağrıkəsici', 'Bayer', '100mg, 300mg', 'Qan dövranı pozuntuları', 'Mədə qanaxması', 'Acetylsalicylic acid'),
                ('Amoxicillin', 'Antibiotik', 'GSK', '250mg, 500mg', 'Penicillin allergiyası', 'Diarrhea', 'Amoxicillin'),
                ('Ibuprofen', 'İltihabəleyhinə', 'Pfizer', '200mg, 400mg', 'Böyrək xəstəliyi', 'Mədə ağrısı', 'Ibuprofen'),
                ('Vitamin D3', 'Vitamin', 'Bayer', '1000IU, 2000IU', 'Hiperkalsemiya', 'Nadir hallarda', 'Cholecalciferol')
            ]
            
            for med in common_medications:
                check_med = "SELECT COUNT(*) FROM medications WHERE name = %s"
                self.cursor.execute(check_med, (med[0],))
                
                if self.cursor.fetchone()['count'] == 0:
                    insert_med = """
                    INSERT INTO medications (name, category, manufacturer, common_dosages, 
                                           contraindications, side_effects, active_ingredient)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """
                    self.cursor.execute(insert_med, med)
            
            self.connection.commit()
            
        except Exception as e:
            print(f"İlkin məlumat əlavə etmə xətası: {e}")
            self.connection.rollback()
    
    def authenticate_doctor(self, username, password):
        """Həkim autentifikasiyası"""
        try:
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            query = """
            SELECT * FROM doctors 
            WHERE username = %s AND password_hash = %s AND is_active = TRUE
            """
            
            self.cursor.execute(query, (username, password_hash))
            doctor = self.cursor.fetchone()
            
            if doctor:
                return dict(doctor)
            return None
            
        except Exception as e:
            print(f"Həkim autentifikasiya xətası: {e}")
            return None
    
    def search_patients(self, search_term):
        """Pasiyent axtarışı"""
        try:
            query = """
            SELECT * FROM patients 
            WHERE name ILIKE %s OR surname ILIKE %s OR id_number ILIKE %s OR phone ILIKE %s
            ORDER BY name, surname
            """
            
            search_pattern = f"%{search_term}%"
            self.cursor.execute(query, (search_pattern, search_pattern, search_pattern, search_pattern))
            
            return [dict(row) for row in self.cursor.fetchall()]
            
        except Exception as e:
            print(f"Pasiyent axtarış xətası: {e}")
            return []
    
    def get_patient_by_id(self, patient_id):
        """Pasiyenti ID ilə tapma"""
        try:
            query = "SELECT * FROM patients WHERE id = %s"
            self.cursor.execute(query, (patient_id,))
            
            patient = self.cursor.fetchone()
            return dict(patient) if patient else None
            
        except Exception as e:
            print(f"Pasiyent tapma xətası: {e}")
            return None
    
    def create_prescription(self, prescription_data):
        """Yeni resept yaratma"""
        try:
            # Resept yaratma
            prescription_query = """
            INSERT INTO prescriptions (doctor_id, patient_id, complaint, diagnosis, notes)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
            """
            
            self.cursor.execute(prescription_query, (
                prescription_data['doctor_id'],
                prescription_data['patient_id'],
                prescription_data['complaint'],
                prescription_data['diagnosis'],
                prescription_data['notes']
            ))
            
            prescription_id = self.cursor.fetchone()['id']
            
            # Dərman elementlərini əlavə etmə
            for item in prescription_data['medications']:
                item_query = """
                INSERT INTO prescription_items 
                (prescription_id, medication_name, dosage, frequency, duration, instructions, quantity)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                
                self.cursor.execute(item_query, (
                    prescription_id,
                    item['medication_name'],
                    item['dosage'],
                    item['frequency'],
                    item['duration'],
                    item['instructions'],
                    item['quantity']
                ))
            
            self.connection.commit()
            return prescription_id
            
        except Exception as e:
            print(f"Resept yaratma xətası: {e}")
            self.connection.rollback()
            return None
    
    def get_patient_prescriptions(self, patient_id):
        """Pasiyentin reseptlərini tapma"""
        try:
            query = """
            SELECT p.*, d.name as doctor_name, d.surname as doctor_surname,
                   d.specialty as doctor_specialty
            FROM prescriptions p
            JOIN doctors d ON p.doctor_id = d.id
            WHERE p.patient_id = %s
            ORDER BY p.prescription_date DESC
            """
            
            self.cursor.execute(query, (patient_id,))
            prescriptions = [dict(row) for row in self.cursor.fetchall()]
            
            # Hər resept üçün dərmanları əlavə et
            for prescription in prescriptions:
                items_query = """
                SELECT * FROM prescription_items 
                WHERE prescription_id = %s
                """
                self.cursor.execute(items_query, (prescription['id'],))
                prescription['medications'] = [dict(row) for row in self.cursor.fetchall()]
            
            return prescriptions
            
        except Exception as e:
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
                total_query += " AND prescription_date BETWEEN %s AND %s"
                self.cursor.execute(total_query, (doctor_id, start_date, end_date))
            else:
                self.cursor.execute(total_query, (doctor_id,))
            
            stats['total_prescriptions'] = self.cursor.fetchone()['total_prescriptions']
            
            # Unikal pasiyent sayı
            patients_query = """
            SELECT COUNT(DISTINCT patient_id) as unique_patients
            FROM prescriptions 
            WHERE doctor_id = %s
            """
            if start_date and end_date:
                patients_query += " AND prescription_date BETWEEN %s AND %s"
                self.cursor.execute(patients_query, (doctor_id, start_date, end_date))
            else:
                self.cursor.execute(patients_query, (doctor_id,))
            
            stats['unique_patients'] = self.cursor.fetchone()['unique_patients']
            
            # Ən çox təyin olunan dərmanlar
            medications_query = """
            SELECT pi.medication_name, COUNT(*) as count
            FROM prescription_items pi
            JOIN prescriptions p ON pi.prescription_id = p.id
            WHERE p.doctor_id = %s
            """
            if start_date and end_date:
                medications_query += " AND p.prescription_date BETWEEN %s AND %s"
                medications_query += " GROUP BY pi.medication_name ORDER BY count DESC LIMIT 10"
                self.cursor.execute(medications_query, (doctor_id, start_date, end_date))
            else:
                medications_query += " GROUP BY pi.medication_name ORDER BY count DESC LIMIT 10"
                self.cursor.execute(medications_query, (doctor_id,))
            
            stats['top_medications'] = [dict(row) for row in self.cursor.fetchall()]
            
            return stats
            
        except Exception as e:
            print(f"Statistika tapma xətası: {e}")
            return {}
    
    def get_medications_list(self):
        """Dərmanlar siyahısını alma"""
        try:
            query = "SELECT * FROM medications ORDER BY name"
            self.cursor.execute(query)
            
            return [dict(row) for row in self.cursor.fetchall()]
            
        except Exception as e:
            print(f"Dərmanlar siyahısı xətası: {e}")
            return []
    
    def get_doctor_by_id(self, doctor_id):
        """Həkimi ID ilə tapma"""
        try:
            query = "SELECT * FROM doctors WHERE id = %s AND is_active = TRUE"
            self.cursor.execute(query, (doctor_id,))
            
            doctor = self.cursor.fetchone()
            return dict(doctor) if doctor else None
            
        except Exception as e:
            print(f"Həkim tapma xətası: {e}")
            return None
    
    def close_connection(self):
        """Verilənlər bazası bağlantısını bağlama"""
        try:
            if self.cursor:
                self.cursor.close()
            if self.connection:
                self.connection.close()
        except Exception as e:
            print(f"Bağlantı bağlama xətası: {e}")