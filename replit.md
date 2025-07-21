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
- 2025-01-21: Tamamilə yeni streamlined workflow sistemi yaradıldı
- 2025-01-21: Köhnə barmaq izi sistemləri silindi və fake progress dialog yaradıldı
- 2025-01-21: Yeni workflow: Fake barmaq izi oxuma → Pasiyent seçimi → AI təhlil → Resept yazma
- 2025-01-21: Pasiyent seçim dialoqu və yeni pasiyent yaratma sistemi tamamlandı
- 2025-01-21: AI təhlil ilə keçmiş reseptlərin analizi və tövsiyələr
- 2025-01-21: Verilənlər bazası strukturu MySQL ingilis dilində düzəldildi
- 2025-01-21: Modern tam ekran giriş sistemi (login: huseyn/huseyn)
- 2025-01-21: Dashboard analitika və statistika sistemi
- 2025-01-21: Gemini AI həkim köməkçisi və chatbot
- 2025-01-21: .env fayl konfiguratsiyası əlavə edildi GEMINI_API_KEY üçün
- 2025-01-21: python-dotenv kitabxanası ilə environment variable idarəetməsi
- 2025-01-21: Professional UI dizayn yeniləməsi - modern gradient rənglər
- 2025-01-21: Segoe UI font və yaxşılaşdırılmış button dizaynları
- 2025-01-21: AI mesajlar HTML formatında düzgün render olunur
- 2025-01-21: Tam Azərbaycan dili interfeys və mesajları
- 2025-01-21: İki AI düyməsi: "Tarixçə Təhlil Et" və "AI Məsləhət Al" 
- 2025-01-21: Keçmiş reseptlərə klik ediləndə detallı məlumat göstərilir
- 2025-01-21: AI mesajları düzgün scroll ilə altda göstərilir
- 2025-01-21: Professional login ekranı - Azərbaycan Səhiyyə Nazirliyi teması
- 2025-01-21: Dashboard header daha professional və informativ edildi

## İstifadəçi Seçimləri
- Dil: Azərbaycan dili (tam interfeys)
- PyQt5 GUI framework (istəkli olaraq saxlanılması)
- Tam ekran aplikasiya görünüşü
- Mavi gradient dizayn teması