Step 1: ESP32 Sensor Node Setup

This folder contains the firmware for the ESP32 board that collects multiple sensor readings and sends them to both a custom backend API and ThingSpeak.

What the Code Does
The file 'esp32_main.ino' reads real-time data from the following sensors:
🌡️ DHT22 – temperature and humidity
🌫️ MQ-135 – air quality (e.g., CO₂)
🔥 MQ-9 – carbon monoxide / LPG
💧 Soil Moisture Sensor
🌧️ Rain Sensor
💧 Water Flow Sensor

The ESP32:
Connects to Wi-Fi
Sends HTTP GET data to a PHP backend API
Updates data to ThingSpeak every 15 seconds

Hardware Required
ESP32 board (NodeMCU or Devkit)
MQ-135, MQ-9 gas sensors
DHT11 sensor
Soil moisture sensor
Rain sensor (analog)
Flow sensor (digital)
Breadboard + jumper wires
USB cable

Pin Configuration

Sensor            ESP32 GPIO Pin 

MQ-135            GPIO 32
MQ-9              GPIO 33
Soil Moisture     GPIO 35
Rain Sensor       GPIO 34
Flow Sensor       GPIO 26
DHT11 (Temp/Hum)  GPIO 14

Setup Instructions

1. Open `esp32_main.ino` in Arduino IDE.

2. Install required libraries:
'DHT sensor library', 'WiFi.h', 'HTTPClient.h', 'EEPROM.h', 'ThingSpeak.h'

3. Replace the code with your own Credentials:-
#define WIFI_SSID "your_wifi_name"
#define WIFI_PASSWORD "your_wifi_password"
#define API_URL "http://192.168.1.100/api.php"
#define THINGSPEAK_CHANNEL 123456
#define THINGSPEAK_API_KEY "ABCDEF1234567890"

I have also attached the circuit diagram for connection purposes. 