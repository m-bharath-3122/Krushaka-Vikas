# 🌱 Krushaka Vikas – Empowering Smart Farming with IoT & Machine Learning

**Krushaka Vikas** is a full-stack smart agriculture platform that leverages IoT sensors, predictive Machine Learning models, and workflow automation to help farmers monitor, predict, and optimise their crop and resource usage with real-time insights.

## 🚨 The Problem:
-  Over 60% of Indian farmers still rely on traditional, manual methods.
-  Lack of timely environmental data leads to poor decisions on irrigation and crop planning.
-  35–45% water overuse, rising carbon exposure, and degraded soil conditions are often left unmonitored.

## ✅ The Solution:
Krushaka Vikas brings a **low-cost yet powerful solution** to the ground:
- 📡 ESP32 IoT device to gather **live data from 6 sensors**
- 🤖 ML models to **forecast humidity, CO₂, and temperature**
- 🧩 Apache Airflow pipelines to automate predictions
- 📊 Metabase dashboards to visualise actionable insights

> 📈 Studies show data-driven irrigation and environmental monitoring can improve yield by 20–35% and reduce water consumption by up to 40%.

## 🧭 Project Structure & Workflow

```bash
krushaka-vikas/
├── 1. ESP-32 Code/         ← Flash sensor firmware to ESP32
├── 2. Backend/             ← PHP API + MySQL DB to collect data
├── 3. Datasets/            ← Raw CSVs for model training
├── 4. ML Models/           ← Jupyter notebooks + .joblib models
├── 5. Airflow/             ← ML automation workflows (DAGs)
├── 6. Metabase/            ← Dashboard & analytics layer
├── 7. Images/              ← Architecture, diagrams, wiring
├── .gitignore              ← Ignore sensitive & generated files
├── LICENSE                 ← MIT License
└── README.md               ← This documentation
```
## 🚶 Execution Order (Step-by-Step Guide)

1. **ESP32 Sensor Code**  
   - Reads real-time data (temp, humidity, gas, soil, rainfall, flow)
   - Sends to your backend and ThingSpeak

2. **Backend PHP API**  
   - Receives and stores ESP32 data into a MySQL database

3. **Datasets**  
   - Includes:
     - `Gas Sensor Measurements Dataset` [📎 cited]
     - My own `tempandhum.csv` (real readings)

4. **ML Models**  
   - Trains and saves models for:
     - CO₂ (from MQ135)
     - CO/smoke (from MQ9)
     - Temp from Humidity
     - Humidity from Temp

5. **Airflow Automation**  
   - Uses Apache Airflow DAGs to schedule ML tasks and pipeline execution  
   - Dockerized Airflow runs on `localhost:1234`

6. **Metabase Visualization**  
   - Dashboard on `localhost:12345` (via Docker)  
   - Tracks trends, forecasts, and sensor behaviours

7. **Images & Architecture**  
   - For wiring diagrams, system layout, and data workflow illustrations

## ⚙️ Tech Stack
                               
 Microcontroller - ESP32 Devkit (Arduino IDE)               
 Sensors         - MQ135, MQ9, DHT22, Soil, Rain, Flow         
 Backend         - PHP + MySQL                                 
 ML              - Python 3.8, scikit-learn, pandas, joblib    
 Automation      - Apache Airflow (Docker Compose)             
 Dashboard       - Metabase (Docker)                           

## 🧾 .gitignore – What Not to Push

Add this file to keep your repo clean:

```
.env
__pycache__/
*.joblib
*.csv
*.log
*.sqlite
*.DS_Store
secrets.h
```

## 💡 Impact & Future Scope

 100% open-source, modular design  
 Can scale to crop health monitoring, irrigation alerts  
 Ideal for schools, NGOs, rural innovation labs

> With just a ₹400 ESP32, farmers can unlock a ₹4000/month increase in optimised water and fertiliser usage with smart alerts.

📬 For doubts or collaborations: raise an issue or drop a message!
