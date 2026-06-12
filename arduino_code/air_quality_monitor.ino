/*
  IoT Air Quality & Pollution Monitoring Dashboard
  ESP32 + MQ135 + DHT11 + ThingSpeak
  -----------------------------------------------
  Reads air quality (MQ135) and temp/humidity (DHT11),
  classifies pollution level, triggers alerts,
  and uploads data to ThingSpeak.
*/

#include <WiFi.h>
#include <HTTPClient.h>
#include "DHT.h"

// ---------- CONFIG ----------
const char* WIFI_SSID     = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";
const char* THINGSPEAK_API_KEY = "YOUR_WRITE_API_KEY";
const char* THINGSPEAK_URL = "http://api.thingspeak.com/update";

// ---------- PIN DEFINITIONS ----------
#define MQ135_PIN   34
#define DHT_PIN     4
#define DHT_TYPE    DHT11
#define BUZZER_PIN  25
#define LED_GREEN   26
#define LED_YELLOW  27
#define LED_RED     14

DHT dht(DHT_PIN, DHT_TYPE);

// ---------- THRESHOLDS ----------
const int AQI_GOOD_MAX     = 1000;  // ADC value
const int AQI_MODERATE_MAX = 2000;
const int AQI_POOR_MAX     = 3000;
// above AQI_POOR_MAX = Hazardous

void setup() {
  Serial.begin(115200);
  dht.begin();

  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(LED_GREEN, OUTPUT);
  pinMode(LED_YELLOW, OUTPUT);
  pinMode(LED_RED, OUTPUT);

  connectWiFi();
}

void connectWiFi() {
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected!");
}

String classifyAirQuality(int mq135Value) {
  if (mq135Value <= AQI_GOOD_MAX) return "Good";
  else if (mq135Value <= AQI_MODERATE_MAX) return "Moderate";
  else if (mq135Value <= AQI_POOR_MAX) return "Poor";
  else return "Hazardous";
}

void setAlertOutputs(String status) {
  // Reset all
  digitalWrite(LED_GREEN, LOW);
  digitalWrite(LED_YELLOW, LOW);
  digitalWrite(LED_RED, LOW);
  digitalWrite(BUZZER_PIN, LOW);

  if (status == "Good") {
    digitalWrite(LED_GREEN, HIGH);
  } else if (status == "Moderate") {
    digitalWrite(LED_YELLOW, HIGH);
  } else if (status == "Poor") {
    digitalWrite(LED_RED, HIGH);
  } else { // Hazardous
    digitalWrite(LED_RED, HIGH);
    digitalWrite(BUZZER_PIN, HIGH);
  }
}

void uploadToThingSpeak(int mq135Value, float temp, float humidity, String status) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi not connected, skipping upload.");
    return;
  }

  HTTPClient http;
  String url = String(THINGSPEAK_URL) +
                "?api_key=" + THINGSPEAK_API_KEY +
                "&field1=" + String(mq135Value) +
                "&field2=" + String(temp) +
                "&field3=" + String(humidity) +
                "&field4=" + status;

  http.begin(url);
  int httpCode = http.GET();
  Serial.println("ThingSpeak response code: " + String(httpCode));
  http.end();
}

void loop() {
  int mq135Value = analogRead(MQ135_PIN);
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();

  if (isnan(temperature) || isnan(humidity)) {
    Serial.println("Failed to read DHT sensor!");
    delay(2000);
    return;
  }

  String status = classifyAirQuality(mq135Value);
  setAlertOutputs(status);

  // Print to Serial Monitor
  Serial.println("---------------------------------");
  Serial.println("MQ135 Value : " + String(mq135Value));
  Serial.println("Temperature : " + String(temperature) + " C");
  Serial.println("Humidity    : " + String(humidity) + " %");
  Serial.println("Air Quality : " + status);
  if (status == "Hazardous") {
    Serial.println("ALERT! Hazardous air quality detected!");
  }

  uploadToThingSpeak(mq135Value, temperature, humidity, status);

  delay(16000); // ThingSpeak free tier: min 15s between updates
}