#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from database.connection import DatabaseConnection

def create_test_data():
    """Test məlumatları yaradır"""
    db = DatabaseConnection()
    
    if not db.connect():
        print("Verilənlər bazası qoşulma xətası!")
        return False
        
    try:
        # Test aptek əlavə et
        pharmacy_query = """
        INSERT IGNORE INTO pharmacies 
        (name, address, phone, email, license_number, username, password, 
         commission_rate, current_month_commission, is_active, payment_status) 
        VALUES 
        ('BioScript Mərkəzi Aptek', 'Bakı şəhəri, Nizami rayonu, 28 May küçəsi 12', 
         '+994503055524', 'info@bioscriptaptek.az', 'PH001', 'aptek1', 'aptek123', 
         3.00, 0.00, 1, 'Unpaid')
        """
        db.execute_query(pharmacy_query)
        print("✓ Test aptek əlavə edildi")
        
        # Test əczaçılar əlavə et  
        staff_query = """
        INSERT IGNORE INTO pharmacy_staff 
        (pharmacy_id, name, role, username, password, is_active) 
        VALUES 
        (1, 'Əli Həsənov', 'Baş Əczaçı', 'ali', 'ali123', 1),
        (1, 'Ayşə Məmmədova', 'Əczaçı', 'ayse', 'ayse123', 1)
        """
        db.execute_query(staff_query)
        print("✓ Test əczaçılar əlavə edildi")
        
        # Test resept əlavə et
        prescription_query = """
        INSERT IGNORE INTO prescriptions 
        (id, doctor_id, patient_id, hospital_id, status, issued_at, expires_at, complaint, diagnosis) 
        VALUES 
        (1, 16, 'PAT171', 6, 'active', NOW(), DATE_ADD(NOW(), INTERVAL 30 DAY), 
         'Baş ağrısı və hərarət', 'Soyuqdəymə')
        """
        db.execute_query(prescription_query)
        print("✓ Test resept əlavə edildi")
        
        # Test dərmanlar əlavə et
        items_query = """
        INSERT IGNORE INTO prescription_items 
        (prescription_id, name, dosage, instructions) 
        VALUES 
        (1, 'Panadol', '500mg', '8 saatda bir - 5 gün'),
        (1, 'Nurofen', '200mg', '12 saatda bir - 3 gün'),
        (1, 'Vitamin C', '1000mg', 'Gündə bir dənə - 10 gün')
        """
        db.execute_query(items_query)
        print("✓ Test dərmanlar əlavə edildi")
        
        print("\n🎉 Bütün test məlumatları uğurla yaradıldı!")
        print("Login məlumatları:")
        print("İstifadəçi adı: ali")
        print("Şifrə: ali123")
        return True
        
    except Exception as e:
        print(f"Test məlumatları yaradarkən xəta: {e}")
        return False
    finally:
        db.disconnect()

if __name__ == "__main__":
    create_test_data()