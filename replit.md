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
- `ui/` - GUI komponentləri (professional dizayn)
- `database/` - Verilənlər bazası əlaqələri
- `models/` - Data modelləri
- `arduino/` - AS608 barmaq izi oxuyucu kodu
- `gemini_ai.py` - AI həkim köməkçisi
- `.env` - API açarları konfiguratsiyası

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
- 2025-01-21: .env fayl konfiguratsiyası əlavə edildi GEMINI_API_KEY üçün
- 2025-01-21: python-dotenv kitabxanası ilə environment variable idarəetməsi
- 2025-01-21: Professional UI dizayn yeniləməsi - modern gradient rənglər
- 2025-01-21: Segoe UI font və yaxşılaşdırılmış button dizaynları
- 2025-01-21: Tam funksional Arduino AS608 kodu və dokumentasiya
- 2025-01-21: Monday ingilis dilindən Azərbaycan dilinə tərcümə edildi
- 2025-01-21: AI mesajlar HTML formatında düzgün render olunur və sıra düzəldildi
- 2025-01-21: Düymələrin eni artırıldı və mətn kəsilməsi problemi həll edildi
- 2025-01-21: Barmaq izi oxuma dialogu professional dizaynda yeniləndi
- 2025-01-21: Yeni workflow sistemi: Barmaq izi → Pasiyent tarixçəsi → Yeni resept
- 2025-01-21: Resept tarixçəsi düyməsi silindi, yalnız fingerprint-first workflow qaldı

## İstifadəçi Seçimləri
- Dil: Azərbaycan dili (tam interfeys)
- PyQt5 GUI framework (istəkli olaraq saxlanılması)
- Tam ekran aplikasiya görünüşü
- Mavi gradient dizayn teması