// ==================================================
// ESP8266 + HC-SR04 + Relay + Button + LCD I2C
// HC-SR04 đo khoảng cách
// Hiển thị Serial + LCD
// Nhấn nút bật/tắt motor
// Tự động tắt motor nếu khoảng cách < 3.5 cm
// ==================================================

#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// ===== LCD I2C =====
LiquidCrystal_I2C lcd(0x27, 16, 2);

// ===== CHÂN =====
#define BUTTON_PIN D5
#define TRIG_PIN   D1
#define ECHO_PIN   D2
#define RELAY_PIN  D7

// ===== BIẾN =====
bool motorState = false;
bool lastButtonState = HIGH;

// ===== NGƯỠNG TẮT MOTOR =====
const float STOP_DISTANCE = 3.5;

// ==================================================
// HÀM ĐỌC HC-SR04
// ==================================================
float readDistance() {

  float total = 0;
  int validSamples = 0;

  for (int i = 0; i < 5; i++) {

    digitalWrite(TRIG_PIN, LOW);
    delayMicroseconds(2);

    digitalWrite(TRIG_PIN, HIGH);
    delayMicroseconds(10);

    digitalWrite(TRIG_PIN, LOW);

    long duration = pulseIn(ECHO_PIN, HIGH, 30000);

    if (duration == 0) {
      continue;
    }

    float distance = duration * 0.034 / 2;

    if (distance > 2 && distance < 400) {
      total += distance;
      validSamples++;
    }

    delay(50);
  }

  if (validSamples == 0) {
    return -1;
  }

  return total / validSamples;
}

// ==================================================
void setup() {

  Serial.begin(115200);

  // ===== HC-SR04 =====
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  // ===== RELAY =====
  pinMode(RELAY_PIN, OUTPUT);

  // Relay OFF lúc khởi động
  // Relay active LOW
  digitalWrite(RELAY_PIN, HIGH);

  // ===== BUTTON =====
  pinMode(BUTTON_PIN, INPUT_PULLUP);

  // ===== LCD =====
  Wire.begin(D3, D4);

  lcd.init();
  lcd.backlight();

  lcd.setCursor(0, 0);
  lcd.print("System Start");

  Serial.println("System Started");

  delay(2000);
  lcd.clear();
}

// ==================================================
void loop() {

  // =====================================
  // ĐỌC KHOẢNG CÁCH
  // =====================================

  float distanceCm = readDistance();

  // =====================================
  // TỰ ĐỘNG TẮT MOTOR
  // =====================================

  if (distanceCm > 0 && distanceCm < STOP_DISTANCE) {

    motorState = false;

    // Relay active LOW
    digitalWrite(RELAY_PIN, HIGH);

    Serial.println("AUTO STOP MOTOR");
  }

  // =====================================
  // SERIAL
  // =====================================

  Serial.print("Distance: ");

  if (distanceCm > 0) {
    Serial.print(distanceCm);
    Serial.println(" cm");
  }
  else {
    Serial.println("Sensor Error");
  }

  // =====================================
  // LCD
  // =====================================

  lcd.clear();

  lcd.setCursor(0, 0);

  if (distanceCm > 0) {

    lcd.print("Dist: ");
    lcd.print(distanceCm, 1);
    lcd.print("cm");

  } else {

    lcd.print("Sensor Error");
  }

  lcd.setCursor(0, 1);

  if (motorState) {
    lcd.print("Motor: ON ");
  }
  else {
    lcd.print("Motor: OFF");
  }

  // =====================================
  // BUTTON
  // =====================================

  bool currentButtonState = digitalRead(BUTTON_PIN);

  if (lastButtonState == HIGH && currentButtonState == LOW) {

    // Chỉ cho bật motor nếu khoảng cách an toàn
    if (distanceCm >= STOP_DISTANCE || distanceCm < 0) {

      motorState = !motorState;

      // Relay active LOW
      digitalWrite(RELAY_PIN, !motorState);

      if (motorState) {
        Serial.println("Motor ON");
      }
      else {
        Serial.println("Motor OFF");
      }

    } else {

      Serial.println("Too Close - Motor Locked");
    }

    delay(300);
  }

  lastButtonState = currentButtonState;

  delay(500);
}