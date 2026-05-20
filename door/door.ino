#include <SPI.h>
#include <MFRC522.h>

// ==========================
// RFID RC522
// ==========================
#define SS_PIN   D2
#define RST_PIN  D1

MFRC522 rfid(SS_PIN, RST_PIN);

// ==========================
// PIN CONFIG
// ==========================
#define BUTTON_PIN D3
#define MC38_PIN   D4
#define BUZZER_PIN D8
#define LED_PIN    D0

// ==========================
// SYSTEM STATE
// ==========================
bool alarmArmed = false;
bool alarmTriggered = false;

bool waitingForRFID = false;

// ==========================
// BUTTON DEBOUNCE
// ==========================
bool lastButtonReading = HIGH;
bool buttonState = HIGH;

unsigned long lastDebounceTime = 0;
const unsigned long debounceDelay = 50;

// ==========================
// DOOR STATE
// ==========================
bool lastDoorState = LOW;

// ==========================
// TIMER
// ==========================
unsigned long alarmDelayStart = 0;
unsigned long lastStatusPrint = 0;
unsigned long lastBlinkTime = 0;
unsigned long lastCountdownPrint = 0;

// ==========================
// DELAY
// ==========================
const unsigned long ENTRY_DELAY = 5000;

// ==========================
// LED
// ==========================
bool ledState = LOW;

// ==========================
// RFID UID HỢP LỆ
// ==========================
byte validUID[4] = {0x00, 0x98, 0x09, 0x1E};

// =====================================================
// SETUP
// =====================================================
void setup() {

  Serial.begin(115200);

  SPI.begin();
  rfid.PCD_Init();

  pinMode(BUZZER_PIN, OUTPUT);

  pinMode(LED_PIN, OUTPUT);

  pinMode(BUTTON_PIN, INPUT_PULLUP);

  // MC38 dùng INPUT_PULLUP
  pinMode(MC38_PIN, INPUT_PULLUP);

  digitalWrite(BUZZER_PIN, LOW);
  digitalWrite(LED_PIN, LOW);

  lastDoorState = digitalRead(MC38_PIN);

  Serial.println();
  Serial.println("===== SYSTEM READY =====");
}

// =====================================================
// LOOP
// =====================================================
void loop() {

  checkButton();

  checkRFID();

  checkDoor();

  handleAlarm();

  handleLED();

  printStatus();
}

// =====================================================
// BUTTON CONTROL
// =====================================================
void checkButton() {

  bool reading = digitalRead(BUTTON_PIN);

  // debounce
  if (reading != lastButtonReading) {

    lastDebounceTime = millis();
  }

  if ((millis() - lastDebounceTime) > debounceDelay) {

    if (reading != buttonState) {

      buttonState = reading;

      // button pressed
      if (buttonState == LOW) {

        alarmArmed = !alarmArmed;

        alarmTriggered = false;
        waitingForRFID = false;

        noTone(BUZZER_PIN);

        if (alarmArmed) {

          Serial.println("ARM ON");

          beepShort();
        }
        else {

          Serial.println("ARM OFF");

          beepShort();
          delay(100);
          beepShort();
        }
      }
    }
  }

  lastButtonReading = reading;
}

// =====================================================
// RFID CHECK
// =====================================================
void checkRFID() {

  if (!rfid.PICC_IsNewCardPresent())
    return;

  if (!rfid.PICC_ReadCardSerial())
    return;

  Serial.print("Card UID: ");

  for (byte i = 0; i < rfid.uid.size; i++) {

    if (rfid.uid.uidByte[i] < 0x10)
      Serial.print("0");

    Serial.print(rfid.uid.uidByte[i], HEX);
    Serial.print(" ");
  }

  Serial.println();

  // Kiểm tra UID
  if (isValidCard()) {

    Serial.println("ACCESS GRANTED");

    alarmArmed = false;
    alarmTriggered = false;
    waitingForRFID = false;

    noTone(BUZZER_PIN);

    beepShort();
    delay(100);
    beepShort();
  }
  else {

    Serial.println("ACCESS DENIED");

    beepLong();
  }

  Serial.println("----------------------");

  rfid.PICC_HaltA();
}

// =====================================================
// CHECK VALID CARD
// =====================================================
bool isValidCard() {

  for (byte i = 0; i < 4; i++) {

    if (rfid.uid.uidByte[i] != validUID[i]) {

      return false;
    }
  }

  return true;
}

// =====================================================
// CHECK DOOR
// =====================================================
void checkDoor() {

  bool currentDoorState = digitalRead(MC38_PIN);

  // LOW = CLOSED
  // HIGH = OPEN

  // Chỉ trigger khi cửa chuyển CLOSED -> OPEN
  if (alarmArmed &&
      !waitingForRFID &&
      !alarmTriggered &&
      lastDoorState == LOW &&
      currentDoorState == HIGH) {

    Serial.println("DOOR OPEN!");
    Serial.println("Waiting RFID for 5 seconds...");

    waitingForRFID = true;

    alarmDelayStart = millis();
  }

  lastDoorState = currentDoorState;
}

// =====================================================
// HANDLE ALARM
// =====================================================
void handleAlarm() {

  // RFID countdown
  if (waitingForRFID) {

    // In countdown mỗi giây
    if (millis() - lastCountdownPrint >= 1000) {

      lastCountdownPrint = millis();

      unsigned long remain =
        (ENTRY_DELAY - (millis() - alarmDelayStart)) / 1000;

      Serial.print("RFID Timeout in: ");
      Serial.print(remain);
      Serial.println("s");
    }

    // Hết thời gian
    if (millis() - alarmDelayStart >= ENTRY_DELAY) {

      waitingForRFID = false;

      alarmTriggered = true;

      Serial.println("!!! ALARM TRIGGERED !!!");
    }
  }

  // Alarm buzzer
  if (alarmTriggered) {

    tone(BUZZER_PIN, 1000);
  }
  else {

    noTone(BUZZER_PIN);
  }
}

// =====================================================
// HANDLE LED
// =====================================================
void handleLED() {

  // ARM OFF
  if (!alarmArmed) {

    digitalWrite(LED_PIN, LOW);
  }

  // ARM ON
  else if (alarmArmed &&
           !waitingForRFID &&
           !alarmTriggered) {

    digitalWrite(LED_PIN, HIGH);
  }

  // Waiting RFID
  else if (waitingForRFID) {

    if (millis() - lastBlinkTime >= 500) {

      lastBlinkTime = millis();

      ledState = !ledState;

      digitalWrite(LED_PIN, ledState);
    }
  }

  // Alarm triggered
  else if (alarmTriggered) {

    if (millis() - lastBlinkTime >= 100) {

      lastBlinkTime = millis();

      ledState = !ledState;

      digitalWrite(LED_PIN, ledState);
    }
  }
}

// =====================================================
// PRINT STATUS
// =====================================================
void printStatus() {

  if (millis() - lastStatusPrint >= 1000) {

    lastStatusPrint = millis();

    bool doorOpen = digitalRead(MC38_PIN);

    Serial.println("===== STATUS =====");

    // ARM
    Serial.print("ARM: ");

    if (alarmArmed)
      Serial.println("ON");
    else
      Serial.println("OFF");

    // Door
    Serial.print("DOOR: ");

    if (doorOpen)
      Serial.println("OPEN");
    else
      Serial.println("CLOSED");

    // RFID WAIT
    Serial.print("WAIT RFID: ");

    if (waitingForRFID)
      Serial.println("YES");
    else
      Serial.println("NO");

    // Alarm
    Serial.print("ALARM: ");

    if (alarmTriggered)
      Serial.println("TRIGGERED");
    else
      Serial.println("NORMAL");

    Serial.println();
  }
}

// =====================================================
// BUZZER FUNCTIONS
// =====================================================
void beepShort() {

  tone(BUZZER_PIN, 2000);

  delay(150);

  noTone(BUZZER_PIN);
}

void beepLong() {

  tone(BUZZER_PIN, 1000);

  delay(700);

  noTone(BUZZER_PIN);
}