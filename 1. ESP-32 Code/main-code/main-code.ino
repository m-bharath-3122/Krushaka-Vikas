#include <Arduino.h>
#include <WiFi.h>
#include <WiFiMulti.h>
#include <HTTPClient.h>
#include <EEPROM.h>
#include <ThingSpeak.h>

#define USE_SERIAL Serial

WiFiMulti wifiMulti;
WiFiClient client;

#include "DHT.h"

#define MQ135 32  //for alcohol
#define MQ9 33    //for carbon monoxide
#define Soil 35   //for Soil
#define DHTPIN 14
#define DHTTYPE DHT22
DHT dht(DHTPIN, DHTTYPE);
#define Rain 34

#define Flow 26
float flowRate;
unsigned long flowMilliLitres;
unsigned long totalMilliLitres;
float totalvolume;
int addr = 0;
float a;

float MQ135val;
float MQ9val;
float Soilval;
float h;
float t;
float Rainval;

string url = "";

// ThingSpeak Configuration
unsigned long myChannelNumber = ******;  // Replace with your Channel Number
const char * myWriteAPIKey = "***************";  // Replace with your Write API Key

// Timer variables for ThingSpeak updates
unsigned long lastTime = 0;
unsigned long timerDelay = 15000;  // Update every 15 seconds (ThingSpeak free limit)

void setup() {

  pinMode(MQ135, INPUT);
  pinMode(MQ9, INPUT);
  pinMode(Soil, INPUT);
  pinMode(Rain, INPUT);
  pinMode(Flow, INPUT);

  dht.begin();
  EEPROM.begin(512);  // Initialize EEPROM

  USE_SERIAL.begin(115200);

  USE_SERIAL.println();
  USE_SERIAL.println();
  USE_SERIAL.println();

  for (uint8_t t = 4; t > 0; t--) {
    USE_SERIAL.printf("[SETUP] WAIT %d...\n", t);
    USE_SERIAL.flush();
    delay(1000);
  }

  wifiMulti.addAP("Your WiFi SSID", "Your WiFi Password");
  
  // Initialize ThingSpeak
  ThingSpeak.begin(client);
}

void loop() {
  url = "paste yourn URL where you have stored your phpscript file";

  Rainval = analogRead(Rain);
  Rainval = map(Rainval, 0, 4095, 0, 100);

  Soilval = analogRead(Soil);
  Soilval = map(Soilval, 0, 4095, 0, 100);

  MQ135val = analogRead(MQ135);
  MQ135val = map(MQ135val, 0, 4095, 0, 100);

  MQ9val = analogRead(MQ9);
  MQ9val = map(MQ9val, 0, 4095, 0, 100);

  float h = dht.readHumidity();
  Serial.print("Humidity: ");
  Serial.print(h);
  Serial.println("%");

  float t = dht.readTemperature();
  Serial.print("Temperature: ");
  Serial.print(t);
  Serial.println("°C");
  Serial.println(MQ135val);
  Serial.println(MQ9val);
  Serial.println(Rainval);
  Serial.println(Soilval);
  

  flowRate = pulseIn(Flow, HIGH);
  flowMilliLitres = (flowRate / 5.5);
  totalMilliLitres += flowMilliLitres;
  totalvolume = totalMilliLitres / 1000;
  Serial.print("Flow rate: ");
  Serial.print(flowRate);
  Serial.print("mL/min");
  Serial.print("  Total volume: ");
  Serial.print(totalvolume);
  Serial.println("L");
  int value = EEPROM.read(addr);
  Serial.println(value);
  EEPROM.write(addr, a + totalvolume);
  delay(10);
  EEPROM.commit();

  // Build URL for your existing server
  url += "?Rainval=" + String(Rainval);
  url += "&Soilval=" + String(Soilval);
  url += "&MQ135val=" + String(MQ135val);
  url += "&MQ9val=" + String(MQ9val);
  url += "&h=" + String(h);
  url += "&t=" + String(t);
  url += "&flowRate=" + String(flowRate);
  url += "&totalvolume=" + String(totalvolume);

  // wait for WiFi connection
  if ((wifiMulti.run() == WL_CONNECTED)) {

    // Send to your existing server
    HTTPClient http;
    USE_SERIAL.print("[HTTP] begin...\n");
    http.begin(url);
    USE_SERIAL.print("[HTTP] GET...\n");
    int httpCode = http.GET();

    if (httpCode > 0) {
      USE_SERIAL.printf("[HTTP] GET... code: %d\n", httpCode);
      if (httpCode == HTTP_CODE_OK) {
        String payload = http.getString();
        USE_SERIAL.println(payload);
      }
    } else {
      USE_SERIAL.printf("[HTTP] GET... failed, error: %s\n", http.errorToString(httpCode).c_str());
    }
    http.end();

    // Send to ThingSpeak (every 15 seconds)
    if ((millis() - lastTime) > timerDelay) {
      // Check for valid sensor readings
      if (!isnan(h) && !isnan(t)) {
        
        // Set the fields with sensor data
        ThingSpeak.setField(1, t);          // Temperature
        ThingSpeak.setField(2, h);          // Humidity  
        ThingSpeak.setField(3, Soilval);    // Soil Moisture
        ThingSpeak.setField(4, Rainval);    // Rain Level
        ThingSpeak.setField(5, MQ135val);   // Air Quality (MQ135)
        ThingSpeak.setField(6, MQ9val);     // Carbon Monoxide
        ThingSpeak.setField(7, flowRate);   // Flow Rate
        ThingSpeak.setField(8, totalvolume); // Total Volume

        // Write multiple fields to ThingSpeak at once
        int x = ThingSpeak.writeFields(myChannelNumber, myWriteAPIKey);
        
        if(x == 200){
          Serial.println("ThingSpeak channel update successful.");
        }
        else{
          Serial.println("Problem updating ThingSpeak channel. HTTP error code " + String(x));
        }
      } else {
        Serial.println("Invalid sensor readings - skipping ThingSpeak update");
      }
      
      lastTime = millis();
    }
  }

  delay(500);
}
