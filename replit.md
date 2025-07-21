# BioScript - Həkim Paneli (Doctor Panel)

## Layihə Xülasəsi
BioScript biometrik səhiyyə idarəetmə sisteminin Həkim Paneli - PyQt5 əsaslı GUI proqramı. Bu sistem AS608 barmaq izi modulundan istifadə edərək pasiyent tanıma, resept yazma, həkim dashboardu və MySQL bazası ilə işləyir.

## Texniki Xüsusiyyətlər
- **GUI Framework**: PyQt5
- **Dil**: Azərbaycan dili interfeysi
- **Verilənlər Bazası**: MySQL (31.186.11.114)
- **Biometrik**: AS608 barmaq izi modulu + server-side NBIS/VeriFinger
- **Platform**: Cross-platform desktop aplikasiya

## Əsas Funksiyalar

### 🩺 Giriş Sistemi
- Həkim giriş paneli (username/password)
- doctors cədvəlindən autentifikasiya
- Hər həkim yalnız öz məlumatlarını görür

### 🧬 Biometrik Tanıma
- AS608 ilə barmaq izi oxunması
- Template base64 formatında MySQL-ə yazılması
- Server-side matching (NBIS/VeriFinger SDK)
- Pasiyent tapılmadıqda yeni qeydiyyat

### 📋 Resept İdarəetməsi
- Barmaq izi ilə pasiyent tanıma
- Yeni resept yazma (şikayət, diaqnoz, dərmanlar)
- prescriptions və prescription_items cədvəlləri

### 🕓 Pasiyent Tarixçəsi
- Tanınmış pasiyentin əvvəlki reseptləri
- Dərman məlumatları və diaqnozlar

### 📊 Həkim Dashboardu
- Günlük/aylıq resept statistikaları
- Vizual qrafiklər (matplotlib/PyQtChart)
- Fəaliyyət analitikası

## Verilənlər Bazası Strukturu
```
doctors - həkimlər (id, username, password, name, ...)
patients - pasiyentlər (id, name, fingerprint_template BLOB, ...)
prescriptions - reseptlər (id, doctor_id, patient_id, complaint, diagnosis, ...)
prescription_items - dərman detalları (id, prescription_id, name, dosage, instructions, ...)
```

## Database Bağlantısı
- Host: 31.186.11.114
- User: bio1criptshop_sayt
- Password: bioscriptsayt
- Database: bio1criptshop_sayt

## Layihə Strukturu
- `main.py` - Əsas həkim paneli GUI
- `database/` - Verilənlər bazası əlaqələri
- `biometric/` - Barmaq izi modulları
- `ui/` - GUI komponentləri

## Son Dəyişikliklər
- 2025-01-20: Layihə başlanğıcı və tələblərin sənədləşdirilməsi

## İstifadəçi Seçimləri
- Dil: Azərbaycan dili (tam interfeys)
- Təhlükəsizlik: Yüksək səviyyəli biometrik və məlumat təhlükəsizliyi
- Performans: Sürətli MySQL sinxronizasiyası