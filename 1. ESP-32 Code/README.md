# 🔌 Step 1: ESP32 Sensor Node Setup

This folder contains the firmware for the ESP32 board that collects multiple sensor readings and sends them to both a custom backend API and ThingSpeak.

## 🧠 What the Code Does

📄 The file **`esp32_main.ino`** reads real-time data from the following sensors:

- 🌡️ **DHT22** – Temperature and humidity  
- 🌫️ **MQ-135** – Air quality (e.g., CO₂)  
- 🔥 **MQ-9** – Carbon monoxide / LPG  
- 💧 **Soil Moisture Sensor**  
- 🌧️ **Rain Sensor**  
- 💧 **Water Flow Sensor**

The ESP32 board:
- Connects to Wi-Fi
- Sends data via **HTTP GET** to a PHP backend
- Pushes updates to **ThingSpeak** every 15 seconds

## 🔌 Hardware Required

- ESP32 board (NodeMCU or DevKit)
- MQ-135 and MQ-9 gas sensors
- DHT22 sensor (temperature + humidity)
- Soil moisture sensor
- Analog rain sensor
- Water flow sensor (digital)
- Breadboard + jumper wires
- USB cable (for programming)

## ⚡ Pin Configuration

**Sensor**            **ESP32 GPIO Pin** 

MQ-135 (Air)          GPIO 32            
MQ-9 (Gas)            GPIO 33            
Soil Moisture         GPIO 35            
Rain Sensor           GPIO 34            
Flow Sensor           GPIO 26            
DHT11 (Temp/Humidity) GPIO 14            

## 🛠️ Setup Instructions

1. Open `esp32_main.ino` in Arduino IDE.

2. Install required libraries:
   - `DHT sensor library`
   - `WiFi.h`
   - `HTTPClient.h`
   - `EEPROM.h`
   - `ThingSpeak.h`

3. Replace the code with your own Credentials:-

   #define WIFI_SSID "your_wifi_name"
   #define WIFI_PASSWORD "your_wifi_password"
   #define API_URL "http://192.168.1.100/api.php"
   #define THINGSPEAK_CHANNEL 123456
   #define THINGSPEAK_API_KEY "ABCDEF1234567890"

I have also attached the circuit diagram for connection purposes.