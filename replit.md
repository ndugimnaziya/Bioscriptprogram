# BioScript - Tibbi Resept İdarəetmə Sistemi

## Layihə Xülasəsi
BioScript - "Səhiyyə Barmaqlarınızın Ucundadır!" sloqanı ilə modern tibbi resept idarəetmə sistemi. PyQt5 əsaslı GUI ilə həkimlər üçün effektiv və təhlükəsiz resept yazma platforması.

## Texniki Xüsusiyyətlər
- **GUI Framework**: PyQt5 (tam ekran interfeys)
- **Dil**: Azərbaycan dili interfeysi
- **Verilənlər Bazası**: MySQL (xarici server)
- **Platform**: Cross-platform desktop aplikasiya
- **Dizayn**: Mavi gradient tema, BioScript korporativ rəngləri

## Əsas Funksiyalar

### 🩺 Həkim Paneli
- Həkim giriş sistemi
- Pasiyent axtarışı və seçimi
- Resept yazma interfeysi
- Resept tarixçəsi

### 📋 Resept İdarəetməsi
- Yeni resept yaratma
- Pasiyent məlumatları
- Dərman təyin etmə
- Dozaj və istifadə qaydaları

### 📊 Analitika
- Günlük/həftəlik/aylıq statistikalar
- Ən çox təyin olunan dərmanlar
- Pasiyent sayı statistikaları

## Layihə Strukturu
- `main.py` - Əsas aplikasiya
- `ui/` - GUI komponentləri
- `database/` - Verilənlər bazası əlaqələri
- `models/` - Data modelləri

## MySQL Verilənlər Bazası
- **Host**: 31.186.11.114
- **Database**: bio1criptshop_sayt
- **Struktur**: Həkimlər, pasiyentlər, reseptlər, xəstəxanalar
- **Test Həkim**: huseyn/huseyn

## Son Dəyişikliklər
- 2025-01-21: Tamamilə yeni BioScript sistemi tamamlandı
- 2025-01-21: Modern tam ekran giriş sistemi (login: huseyn/huseyn)
- 2025-01-21: Dashboard analitika və statistika sistemi
- 2025-01-21: Arduino AS608 barmaq izi oxuyucu inteqrasiyası
- 2025-01-21: Gemini AI həkim köməkçisi və chatbot
- 2025-01-21: Resept yazma workflow sistemi (barmaq izi → tarixçə → yeni resept)

## İstifadəçi Seçimləri
- Dil: Azərbaycan dili (tam interfeys)
- PyQt5 GUI framework (istəkli olaraq saxlanılması)
- Tam ekran aplikasiya görünüşü
- Mavi gradient dizayn teması