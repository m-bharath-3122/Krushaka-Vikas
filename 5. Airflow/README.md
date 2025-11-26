# 🛠️ Step 5: ML Automation with Apache Airflow

This folder automates the retraining and prediction workflows for all trained ML models using **Apache Airflow 2.7.3**.

##  What This Does

- Automates model predictions on sensor data
- Runs retraining jobs on schedule or new data arrival
- Saves predicted results into a database or downstream system

## 📁 Folder Contents

### 📂 dags/
Each DAG handles automation for one sensor:
- `mq9dag.py` – CO/Smoke prediction using MQ9 model
- `mq135dag.py` – CO₂ prediction using MQ135 model
- `temperaturwdag.py` – Temperature prediction from humidity
- `humiditydag.py` – Humidity prediction from temperature

### 📂 docker/
- `docker-compose.yml` → Spin up Airflow 2.7.3 with all services

## 🐳 How to Set Up and Run Airflow with Docker

- Use the Docker file from the URL mentioned in the website for latest file
- I have used Airflow 2.7.3 and after tuning i have attached the file 
- Just replace the docker-compose file with the attached version of mine
- Follow the exact steps as mentioned in the link mentioned below
- https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html 

## 🔁 How the DAGs Work

- Each DAG is triggered based on a schedule or manually
- It loads the relevant `.joblib` model (from `../4_ml-models/models/`)
- Reads the data source (CSV, live DB, or API)
- Performs prediction
- Logs or saves results