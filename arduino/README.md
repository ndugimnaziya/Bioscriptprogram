# BioScript AS608 Barmaq İzi Oxuyucu

Arduino Nano/Uno üçün AS608 barmaq izi sensor inteqrasiyası.

## Hardware Bağlantıları

### AS608 Sensor bağlantıları:
- AS608 VCC → Arduino 5V
- AS608 GND → Arduino GND  
- AS608 TX → Arduino Pin 2
- AS608 RX → Arduino Pin 3
- LED → Arduino Pin 13 (status)

### Komponenlər:
- Arduino Nano və ya Uno
- AS608 Barmaq İzi Sensoru
- Jumper kabellər
- LED (status üçün)
- 220Ω rezistor (LED üçün)

## Quraşdırma

1. Arduino IDE-ni açın
2. AS608_Fingerprint.ino faylını yükləyin
3. Board tipini seçin (Arduino Nano/Uno)
4. Portu seçin
5. Upload edin

## İstifadə

### Serial Monitor Komandaları:

```
ENROLL:ID    - Yeni barmaq qeydiyyatı (ID: 1-200)
SEARCH       - Barmaq axtarışı  
DELETE:ID    - Barmağı silmə
COUNT        - Qeydiyyatlı barmaqların sayı
CLEAR        - Bütün barmaqları silmə
```

### Cavab Formatları:

```
SUCCESS:ENROLLED_ID_123     - Barmaq qeydiyyatı uğurlu
SUCCESS:FOUND_ID_123_CONFIDENCE_95 - Barmaq tapıldı
ERROR:Barmaq tapılmadı      - Barmaq bazada yoxdur
COUNT:15                    - 15 barmaq qeydiyyatlı
```

## Python İnteqrasiyası

BioScript sistemi bu Arduino kodunu Python serial communication ilə istifadə edir:

```python
import serial

# Arduino ilə əlaqə
ser = serial.Serial('COM3', 9600)  # Port dəyişin

# Barmaq qeydiyyatı
ser.write(b'ENROLL:1\n')
response = ser.readline().decode()

# Barmaq axtarışı  
ser.write(b'SEARCH\n')
response = ser.readline().decode()
```

## Status LED

- 2 dəfə yanıb-sön: Sistem hazır
- 3 dəfə yanıb-sön: Qeydiyyat uğurlu
- 1 dəfə uzun yanma: Barmaq tapıldı
- 4 dəfə sürətli: Barmaq tapılmadı
- 5 dəfə sürətli (daimi): Sensor xətası

## Texniki Xüsusiyyətlər

- Baud Rate: 57600 (sensor) / 9600 (serial)
- Yaddaş: 200 barmaq izi
- Axtarış vaxtı: <1 saniyə
- FAR: <0.001%
- FRR: <0.1%
- Gərginlik: 3.3V-5V
- Cərəyan: <120mA

## Troubleshooting

**Sensor tapılmır:**
- Bağlantıları yoxlayın
- 5V power supply istifadə edin
- TX/RX pinləri düz bağlandığından əmin olun

**Barmaq qeyd olunmur:**
- Barmağı təmiz və quru saxlayın
- Sensoru yumuşaq parça ilə silin
- Barmağı tam üzərinə qoyun

**Axtarış işləmir:**
- Barmağın qeydiyyatlı olduğundan əmin olun
- Eyni barmağı istifadə edin
- Sensor səthinin təmiz olduğunu yoxlayın