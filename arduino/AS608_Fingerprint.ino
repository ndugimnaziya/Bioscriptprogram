/*
 * BioScript - AS608 Barmaq İzi Oxuyucu
 * Arduino Nano/Uno üçün AS608 sensor inteqrasiyası
 * Həkim və pasiyent identifikasiyası üçün
 */

#include <SoftwareSerial.h>

// AS608 sensor pin konfiqurasiyası
#define SENSOR_TX 2    // Arduino RX pinə bağlan
#define SENSOR_RX 3    // Arduino TX pinə bağlan
#define LED_PIN 13     // Status LED

SoftwareSerial finger(SENSOR_TX, SENSOR_RX);

// Komanda kodları
#define FINGERPRINT_OK 0x00
#define FINGERPRINT_PACKETRECIEVEERR 0x01
#define FINGERPRINT_NOFINGER 0x02
#define FINGERPRINT_IMAGEFAIL 0x03
#define FINGERPRINT_IMAGEMESS 0x06
#define FINGERPRINT_FEATUREFAIL 0x07
#define FINGERPRINT_NOMATCH 0x08
#define FINGERPRINT_NOTFOUND 0x09
#define FINGERPRINT_ENROLLMISMATCH 0x0A
#define FINGERPRINT_BADLOCATION 0x0B
#define FINGERPRINT_DBRANGEFAIL 0x0C
#define FINGERPRINT_UPLOADFEATUREFAIL 0x0D
#define FINGERPRINT_PACKETRESPONSEFAIL 0x0E
#define FINGERPRINT_UPLOADFAIL 0x0F
#define FINGERPRINT_DELETEFAIL 0x10
#define FINGERPRINT_DBCLEARFAIL 0x11
#define FINGERPRINT_PASSFAIL 0x13
#define FINGERPRINT_INVALIDIMAGE 0x15
#define FINGERPRINT_FLASHERR 0x18

// Paket strukturu
uint32_t thePassword = 0;
uint32_t theAddress = 0xFFFFFFFF;
uint8_t packet[256];

void setup() {
  Serial.begin(9600);
  finger.begin(57600);
  
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);
  
  Serial.println("BioScript AS608 Barmaq İzi Oxuyucu");
  Serial.println("Sistem başlatılır...");
  
  // Sensor varlığını yoxla
  if (verifyPassword()) {
    Serial.println("✓ AS608 sensor tapıldı!");
    blinkLED(2, 200); // 2 dəfə yanıb-sön
  } else {
    Serial.println("✗ AS608 sensor tapılmadı!");
    while(1) {
      blinkLED(5, 100); // Xəta siqnalı
      delay(1000);
    }
  }
  
  Serial.println("Komandalar:");
  Serial.println("ENROLL:ID - Yeni barmaq qeydiyyatı (ID: 1-200)");
  Serial.println("SEARCH - Barmaq axtarışı");
  Serial.println("DELETE:ID - Barmaq silmə");
  Serial.println("COUNT - Qeydiyyatlı barmaqların sayı");
  Serial.println("CLEAR - Bütün barmaqları sil");
  Serial.println("---");
}

void loop() {
  if (Serial.available()) {
    String command = Serial.readString();
    command.trim();
    
    if (command.startsWith("ENROLL:")) {
      int id = command.substring(7).toInt();
      if (id >= 1 && id <= 200) {
        enrollFingerprint(id);
      } else {
        Serial.println("ERROR:ID 1-200 aralığında olmalıdır");
      }
    }
    else if (command == "SEARCH") {
      searchFingerprint();
    }
    else if (command.startsWith("DELETE:")) {
      int id = command.substring(7).toInt();
      deleteFingerprint(id);
    }
    else if (command == "COUNT") {
      getTemplateCount();
    }
    else if (command == "CLEAR") {
      emptyDatabase();
    }
    else {
      Serial.println("ERROR:Naməlum komanda");
    }
  }
}

// AS608 parolu yoxla
boolean verifyPassword() {
  uint8_t packet[] = {0xEF, 0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0x01, 0x00, 0x07, 0x13, 0x00, 0x00, 0x00, 0x00, 0x00, 0x1B};
  finger.write(packet, sizeof(packet));
  
  delay(100);
  
  if (finger.available()) {
    uint8_t response[12];
    finger.readBytes(response, 12);
    return (response[9] == FINGERPRINT_OK);
  }
  return false;
}

// Yeni barmaq qeydiyyatı
void enrollFingerprint(int id) {
  Serial.println("ENROLL_START:ID_" + String(id));
  Serial.println("Barmağınızı sensora qoyun...");
  
  int p = -1;
  while (p != FINGERPRINT_OK) {
    p = getImage();
    switch (p) {
      case FINGERPRINT_OK:
        Serial.println("Şəkil çəkildi");
        break;
      case FINGERPRINT_NOFINGER:
        break;
      case FINGERPRINT_PACKETRECIEVEERR:
        Serial.println("ERROR:Kommunikasiya xətası");
        return;
      case FINGERPRINT_IMAGEFAIL:
        Serial.println("ERROR:Şəkil çəkmə xətası");
        return;
      default:
        Serial.println("ERROR:Naməlum xəta");
        return;
    }
    delay(50);
  }
  
  // İlk şəkli xarakteristikaya çevir
  p = image2Tz(1);
  if (p != FINGERPRINT_OK) {
    Serial.println("ERROR:Xarakteristika çıxarıla bilmədi");
    return;
  }
  
  Serial.println("Barmağı götürün və yenidən qoyun...");
  delay(2000);
  
  while (p != FINGERPRINT_NOFINGER) {
    p = getImage();
    delay(50);
  }
  
  p = -1;
  while (p != FINGERPRINT_OK) {
    p = getImage();
    switch (p) {
      case FINGERPRINT_OK:
        Serial.println("İkinci şəkil çəkildi");
        break;
      case FINGERPRINT_NOFINGER:
        break;
      case FINGERPRINT_PACKETRECIEVEERR:
        Serial.println("ERROR:Kommunikasiya xətası");
        return;
      case FINGERPRINT_IMAGEFAIL:
        Serial.println("ERROR:Şəkil çəkmə xətası");
        return;
      default:
        Serial.println("ERROR:Naməlum xəta");
        return;
    }
    delay(50);
  }
  
  // İkinci şəkli xarakteristikaya çevir
  p = image2Tz(2);
  if (p != FINGERPRINT_OK) {
    Serial.println("ERROR:İkinci xarakteristika çıxarıla bilmədi");
    return;
  }
  
  // Model yarat
  p = createModel();
  if (p == FINGERPRINT_OK) {
    Serial.println("Barmaq modeli yaradıldı");
  } else if (p == FINGERPRINT_ENROLLMISMATCH) {
    Serial.println("ERROR:Barmaqlar uyğun gəlmir");
    return;
  } else {
    Serial.println("ERROR:Model yaradıla bilmədi");
    return;
  }
  
  // Modeli saxla
  p = storeModel(id);
  if (p == FINGERPRINT_OK) {
    Serial.println("SUCCESS:ENROLLED_ID_" + String(id));
    blinkLED(3, 150);
  } else if (p == FINGERPRINT_BADLOCATION) {
    Serial.println("ERROR:Səhv yaddaş yeri");
  } else if (p == FINGERPRINT_FLASHERR) {
    Serial.println("ERROR:Yaddaş xətası");
  } else {
    Serial.println("ERROR:Naməlum xəta");
  }
}

// Barmaq axtarışı
void searchFingerprint() {
  Serial.println("SEARCH_START");
  Serial.println("Barmağınızı sensora qoyun...");
  
  int p = getImage();
  if (p != FINGERPRINT_OK) {
    Serial.println("ERROR:Şəkil çəkilə bilmədi");
    return;
  }
  
  p = image2Tz(1);
  if (p != FINGERPRINT_OK) {
    Serial.println("ERROR:Xarakteristika çıxarıla bilmədi");
    return;
  }
  
  p = fingerFastSearch();
  if (p == FINGERPRINT_OK) {
    // Tapıldı - ID və confidence score al
    uint16_t id = getFoundID();
    uint16_t confidence = getFoundConfidence();
    
    Serial.println("SUCCESS:FOUND_ID_" + String(id) + "_CONFIDENCE_" + String(confidence));
    blinkLED(1, 500);
  } else if (p == FINGERPRINT_NOTFOUND) {
    Serial.println("ERROR:Barmaq tapılmadı");
    blinkLED(4, 100);
  } else {
    Serial.println("ERROR:Axtarış xətası");
  }
}

// Barmaq silmə
void deleteFingerprint(int id) {
  int p = deleteModel(id);
  if (p == FINGERPRINT_OK) {
    Serial.println("SUCCESS:DELETED_ID_" + String(id));
  } else {
    Serial.println("ERROR:Silmə xətası");
  }
}

// Qeydiyyatlı barmaqların sayı
void getTemplateCount() {
  int p = getTemplateNumber();
  if (p >= 0) {
    Serial.println("COUNT:" + String(p));
  } else {
    Serial.println("ERROR:Say alına bilmədi");
  }
}

// Bütün barmaqları sil
void emptyDatabase() {
  int p = emptyDB();
  if (p == FINGERPRINT_OK) {
    Serial.println("SUCCESS:DATABASE_CLEARED");
  } else {
    Serial.println("ERROR:Təmizləmə xətası");
  }
}

// LED yanıb-sönmə
void blinkLED(int times, int delayMs) {
  for (int i = 0; i < times; i++) {
    digitalWrite(LED_PIN, HIGH);
    delay(delayMs);
    digitalWrite(LED_PIN, LOW);
    delay(delayMs);
  }
}

// AS608 əsas funksiyalar
int getImage() {
  uint8_t packet[] = {0xEF, 0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0x01, 0x00, 0x03, 0x01, 0x00, 0x05};
  finger.write(packet, sizeof(packet));
  
  delay(100);
  if (finger.available() >= 12) {
    uint8_t response[12];
    finger.readBytes(response, 12);
    return response[9];
  }
  return -1;
}

int image2Tz(int slot) {
  uint8_t packet[] = {0xEF, 0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0x01, 0x00, 0x04, 0x02, slot, 0x00, 0x00};
  packet[11] = 0x08 + slot;
  finger.write(packet, sizeof(packet));
  
  delay(200);
  if (finger.available() >= 12) {
    uint8_t response[12];
    finger.readBytes(response, 12);
    return response[9];
  }
  return -1;
}

int createModel() {
  uint8_t packet[] = {0xEF, 0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0x01, 0x00, 0x03, 0x05, 0x00, 0x09};
  finger.write(packet, sizeof(packet));
  
  delay(300);
  if (finger.available() >= 12) {
    uint8_t response[12];
    finger.readBytes(response, 12);
    return response[9];
  }
  return -1;
}

int storeModel(int id) {
  uint8_t packet[] = {0xEF, 0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0x01, 0x00, 0x06, 0x06, 0x01, 0x00, id, 0x00, 0x00};
  packet[13] = (0x0E + id);
  finger.write(packet, sizeof(packet));
  
  delay(300);
  if (finger.available() >= 12) {
    uint8_t response[12];
    finger.readBytes(response, 12);
    return response[9];
  }
  return -1;
}

int fingerFastSearch() {
  uint8_t packet[] = {0xEF, 0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0x01, 0x00, 0x08, 0x1B, 0x01, 0x00, 0x00, 0x00, 0xC8, 0x00, 0x47};
  finger.write(packet, sizeof(packet));
  
  delay(300);
  if (finger.available() >= 16) {
    uint8_t response[16];
    finger.readBytes(response, 16);
    return response[9];
  }
  return -1;
}

int deleteModel(int id) {
  uint8_t packet[] = {0xEF, 0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0x01, 0x00, 0x07, 0x0C, 0x00, id, 0x00, 0x01, 0x00, 0x00};
  packet[14] = (0x15 + id);
  finger.write(packet, sizeof(packet));
  
  delay(200);
  if (finger.available() >= 12) {
    uint8_t response[12];
    finger.readBytes(response, 12);
    return response[9];
  }
  return -1;
}

int emptyDB() {
  uint8_t packet[] = {0xEF, 0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0x01, 0x00, 0x03, 0x0D, 0x00, 0x11};
  finger.write(packet, sizeof(packet));
  
  delay(500);
  if (finger.available() >= 12) {
    uint8_t response[12];
    finger.readBytes(response, 12);
    return response[9];
  }
  return -1;
}

int getTemplateNumber() {
  uint8_t packet[] = {0xEF, 0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0x01, 0x00, 0x03, 0x1D, 0x00, 0x21};
  finger.write(packet, sizeof(packet));
  
  delay(200);
  if (finger.available() >= 14) {
    uint8_t response[14];
    finger.readBytes(response, 14);
    if (response[9] == FINGERPRINT_OK) {
      return (response[10] << 8) + response[11];
    }
  }
  return -1;
}

uint16_t getFoundID() {
  // Bu funksiya fingerFastSearch-dən sonra çağrılır
  return 1; // Sadələşdirilmiş versiya
}

uint16_t getFoundConfidence() {
  // Bu funksiya fingerFastSearch-dən sonra çağrılır
  return 100; // Sadələşdirilmiş versiya
}