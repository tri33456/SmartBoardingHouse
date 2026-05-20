#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClient.h>

#include <DHT.h>
#include <PZEM004Tv30.h>
#include <SoftwareSerial.h>

#define DHTPIN D4
#define DHTTYPE DHT11

#define FLOW_SENSOR D6

#define MQ2_PIN A0

// =========================
// GAS THRESHOLD
// =========================
const int GAS_THRESHOLD = 500;

DHT dht(DHTPIN, DHTTYPE);

// =========================
// PZEM
// =========================
SoftwareSerial pzemSWSerial(D2, D1);
PZEM004Tv30 pzem(pzemSWSerial);

// =========================
// WiFi
// =========================
const char* ssid = "Minh Thai";
const char* password = "0967152540Thai@";

const char* serverUrl = "http://192.168.1.131:8000/update-sensor";

// =========================
// Flow Sensor
// =========================
volatile int pulseCount = 0;

float flowRate = 0;
float totalLitres = 0;

// =========================
// Variables
// =========================
float temperature = 0;
float humidity = 0;

int gasValue = 0;

unsigned long previousMillis = 0;

// =========================
// Interrupt đếm xung
// =========================
void ICACHE_RAM_ATTR pulseCounter() {
  pulseCount++;
}

void setup() {

  Serial.begin(115200);

  dht.begin();

  // =========================
  // Flow Sensor
  // =========================
  pinMode(FLOW_SENSOR, INPUT_PULLUP);

  attachInterrupt(digitalPinToInterrupt(FLOW_SENSOR), pulseCounter, FALLING);

  // =========================
  // Kết nối WiFi
  // =========================
  WiFi.begin(ssid, password);

  Serial.print("Connecting WiFi");

  while (WiFi.status() != WL_CONNECTED) {

    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWiFi Connected");
  Serial.println(WiFi.localIP());
}

void loop() {

  // =========================
  // Đọc DHT11
  // =========================
  temperature = dht.readTemperature();
  humidity = dht.readHumidity();

  // =========================
  // Đọc MQ2
  // =========================
  gasValue = analogRead(MQ2_PIN);

  // =========================
  // Tính lưu lượng nước
  // =========================
  if (millis() - previousMillis >= 1000) {

    detachInterrupt(digitalPinToInterrupt(FLOW_SENSOR));

    flowRate = pulseCount / 7.5;

    float litresPerSecond = flowRate / 60.0;

    totalLitres += litresPerSecond;

    pulseCount = 0;

    previousMillis = millis();

    attachInterrupt(digitalPinToInterrupt(FLOW_SENSOR), pulseCounter, FALLING);
  }

  // =========================
  // Đọc PZEM
  // =========================
  float voltage = pzem.voltage();
  float current = pzem.current();
  float power = pzem.power();
  float energy = pzem.energy();

  // =========================
  // Cảnh báo gas
  // =========================

  Serial.print("Gas: ");
  Serial.println(gasValue);

  bool gasDetected = gasValue > GAS_THRESHOLD;

  if (gasDetected) {

    Serial.println("WARNING: GAS DETECTED!");

  } else {

    Serial.println("STATUS: NORMAL");
  }

  // =========================
  // Hiển thị Serial
  // =========================
  Serial.println("========== DATA ==========");

  Serial.print("Temperature: ");
  Serial.print(temperature);
  Serial.println(" *C");

  Serial.print("Humidity: ");
  Serial.print(humidity);
  Serial.println(" %");

  Serial.print("Gas Value: ");
  Serial.println(gasValue);

  if (gasDetected) {
    Serial.println("STATUS: GAS ALERT");
  } else {
    Serial.println("STATUS: NORMAL");
  }

  Serial.print("Flow Rate: ");
  Serial.print(flowRate);
  Serial.println(" L/min");

  Serial.print("Total Water: ");
  Serial.print(totalLitres);
  Serial.println(" L");

  Serial.print("Voltage: ");
  Serial.print(voltage);
  Serial.println(" V");

  Serial.print("Current: ");
  Serial.print(current);
  Serial.println(" A");

  Serial.print("Power: ");
  Serial.print(power);
  Serial.println(" W");

  Serial.print("Energy: ");
  Serial.print(energy);
  Serial.println(" kWh");

  // =========================
  // Gửi dữ liệu lên server
  // =========================
  if (WiFi.status() == WL_CONNECTED) {

    WiFiClient client;
    HTTPClient http;

    http.begin(client, serverUrl);

    http.addHeader("Content-Type", "application/json");

    String jsonData = "{";

    jsonData += "\"room_id\":1,";
    jsonData += "\"temperature\":" + String(temperature) + ",";
    jsonData += "\"humidity\":" + String(humidity) + ",";
    jsonData += "\"gas\":" + String(gasValue) + ",";
    jsonData += "\"flow_rate\":" + String(flowRate) + ",";
    jsonData += "\"total_water\":" + String(totalLitres) + ",";
    jsonData += "\"voltage\":" + String(voltage) + ",";
    jsonData += "\"current\":" + String(current) + ",";
    jsonData += "\"power\":" + String(power) + ",";
    jsonData += "\"energy\":" + String(energy);

    jsonData += "}";

    int httpResponseCode = http.POST(jsonData);

    Serial.print("HTTP Response code: ");
    Serial.println(httpResponseCode);

    http.end();
  }

  delay(2000);
}