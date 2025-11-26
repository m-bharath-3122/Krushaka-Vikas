# Step 3: Datasets Used for Training

This folder contains the two datasets used in the Krushaka Vikas project to train and evaluate machine learning models. These represent both real-time sensor data collected from the ESP32 device and public gas sensor readings.

## 📁 Files Included
                    
'tempandhumidity.csv' - Collected from ESP32 + DHT11 (on-field data) 
'Gas_Sensors_Measurements.csv' - Public dataset for gas sensor training

## 📚 Dataset Details

### 1. 🌡️ Temperature & Humidity Dataset
- **Source**: Collected using DHT22 sensor connected to ESP32
- **Description**: Timestamped records of temperature (°C) and humidity (%)
- **Purpose**: Trains ML models for environmental monitoring
- **File**: `tempandhumidity.csv`

 This dataset was created during the Krushaka Vikas project using real-time sensor deployments.

### 2. 🧪 Gas Sensor Measurement Dataset
- **Author**: Koustav Kumar Mondal  
- **DOI**: [10.5281/zenodo.13283720](https://doi.org/10.5281/zenodo.13283720)  
- **GitHub**: [Gas Sensors Measurements Dataset](https://github.com/TakMashhido/Gas-Sensors-Measurements-Dataset)  
- **Version**: 1.0.0  
- **Date Released**: August 9, 2024  
- **Purpose**: Trains gas detection models (e.g., CO₂, CO)

📌 If you use this dataset, please cite it as below:
 Koustav Kumar Mondal, Gas Sensor Measurement, Zenodo, 2024, DOI: 10.5281/zenodo.13283720

## 🔁 Preprocessing Info

 Raw analog readings are normalized to a 0–100 scale before training.
 This normalization is handled inside the training scripts, not in the CSVs.