#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymysql
from decimal import Decimal

# Database connection məlumatları
DB_CONFIG = {
    'host': '31.186.11.114',
    'user': 'bio1criptshop_sayt',
    'password': 'bioscriptsayt',
    'database': 'bio1criptshop_sayt',
    'charset': 'utf8mb4'
}

def test_dispensing_logs():
    """Dispensing logs cədvəlini yoxla"""
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        print("=== DISPENSING LOGS TEST ===")
        
        # Cədvəl strukturunu göstər
        cursor.execute("DESCRIBE dispensing_logs")
        structure = cursor.fetchall()
        print("Dispensing logs cədvəl strukturu:")
        for field in structure:
            print(f"  {field['Field']} - {field['Type']}")
        
        # Son dispensing logs
        cursor.execute("""
            SELECT * FROM dispensing_logs 
            ORDER BY dispensed_at DESC 
            LIMIT 5
        """)
        recent_logs = cursor.fetchall()
        
        print(f"Son 5 dispensing log:")
        for log in recent_logs:
            print(f"ID: {log['id']}, Pharmacy: {log['pharmacy_id']}, Price: {log['total_price']}, Commission: {log['commission_amount']}, Date: {log['dispensed_at']}")
        
        # Pharmacy ID məlumatlarını yoxla
        cursor.execute("SELECT DISTINCT pharmacy_id FROM dispensing_logs")
        pharmacy_ids = cursor.fetchall()
        print(f"\nMövcud Pharmacy ID-lər: {[p['pharmacy_id'] for p in pharmacy_ids]}")
        
        # Pharmacy cədvəlini yoxla
        cursor.execute("SELECT id, name FROM pharmacies LIMIT 5")
        pharmacies = cursor.fetchall()
        print(f"Pharmacy cədvəli:")
        for ph in pharmacies:
            print(f"  ID: {ph['id']}, Ad: {ph['name']}")
        
        # Hər pharmacy ID üçün statistika
        for pid in pharmacy_ids:
            cursor.execute("""
                SELECT 
                    COUNT(*) as count,
                    SUM(total_price) as total_sales,
                    SUM(commission_amount) as total_commission
                FROM dispensing_logs 
                WHERE pharmacy_id = %s
                AND YEAR(dispensed_at) = YEAR(CURDATE()) 
                AND MONTH(dispensed_at) = MONTH(CURDATE())
            """, (pid['pharmacy_id'],))
            stats = cursor.fetchone()
            print(f"\nPharmacy ID {pid['pharmacy_id']} statistikası:")
            print(f"  Satış sayı: {stats['count']}")
            print(f"  Yekun satış: {stats['total_sales']} AZN")
            print(f"  Yekun komisyon: {stats['total_commission']} AZN")
            print(f"  BioScript borc (3%): {float(stats['total_sales'] or 0) * 0.03:.2f} AZN")
        month_stats = cursor.fetchone()
        
        # Ali istifadəçisinin məlumatlarını yoxla
        cursor.execute("""
            SELECT ps.*, p.name as pharmacy_name, p.id as pharmacy_id
            FROM pharmacy_staff ps
            JOIN pharmacies p ON ps.pharmacy_id = p.id
            WHERE ps.username = 'ali'
        """)
        ali_user = cursor.fetchone()
        if ali_user:
            print(f"\nAli istifadəçisi məlumatları:")
            print(f"  Username: {ali_user['username']}")
            print(f"  Pharmacy ID: {ali_user['pharmacy_id']}")
            print(f"  Pharmacy Name: {ali_user['pharmacy_name']}")
            
            # Ali-nin pharmacy_id-sini 9-a yenilə (satış burada qeydiyyatdan keçib)
            cursor.execute("UPDATE pharmacy_staff SET pharmacy_id = 9 WHERE username = 'ali'")
            cursor.execute("UPDATE pharmacy_staff SET pharmacy_id = 9 WHERE username = 'rena'") 
            conn.commit()
            print("  Ali və Rena istifadəçiləri Pharmacy ID 9-a köçürüldü")
        
        conn.close()
        
    except Exception as e:
        print(f"Xəta: {e}")

if __name__ == "__main__":
    test_dispensing_logs()