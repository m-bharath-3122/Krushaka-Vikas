# 🤖 Step 4: Train and Save ML Models

This folder contains everything related to training and saving machine learning models used in the Krushaka Vikas project.

## 💡 What’s Inside?

### 🔬 scripts
- Contains all the training notebooks for each model.
- Python scripts:
  - `tempandtrail.py` → Trains both humidity-from-temp and temp-from-humidity models
  - `mq9.py` → Random Forest model for MQ9 sensor
  - `mq135.py` → Forecast model for MQ135
- These files include:
  - Dataset loading
  - Preprocessing (like scaling/mapping)
  - Training using scikit-learn
  - Model evaluation and saving

### 💾 models/
- This folder stores `.joblib` files (pretrained models), which are later used by Airflow DAGs or prediction pipelines.

## 📚 Description of Models

File Name                                

`co2_forecast_model.joblib` - Predicts CO₂ levels (from MQ135 sensor)
`mq9_random_forest_model.joblib` - Predicts CO/Smoke levels (from MQ9)
`humidity_from_temperature_rf_model.joblib` - Predicts Humidity from Temperature
`temperature_from_humidity_rf_model.joblib` - Predicts Temperature from Humidity

## 🚀 How to Run Training

1. Open any `.ipynb` file from the `scripts/` folder
2. Run all cells
3. Trained model will be saved to `models/` folder using `joblib.dump()`

## 🧰 Requirements

Install these Python libraries before running:
```bash
pip install pandas numpy scikit-learn joblib
