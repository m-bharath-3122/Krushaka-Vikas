"""
MQ9 Prediction from IoT Sensors ETL Pipeline
Author: Bharath M
Date: October 2025

"""
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import joblib
import pandas as pd
import mysql.connector
from mysql.connector import Error
import logging
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_CONFIG = {
    'host': 'Your server IP',
    'user': 'Your Server username',
    'password': 'Your database Credentials',
    'database': 'Your database id',
    'port': 3306,
    'charset': 'utf8mb4',
    'raise_on_warnings': True,
    'autocommit': False,
    'connect_timeout': 30
}

MODEL_PATH = "/opt/airflow/models/mq9_random_forest_model.joblib"

def extract_sensor_data(**kwargs):
    logger.info("="*60)
    logger.info("STARTING SENSOR DATA EXTRACTION (Recent Data Only)")
    logger.info("="*60)

    connection = None
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT id, Temperature, Humidity, MQ9, Time 
            FROM Data_Collection
            WHERE Temperature IS NOT NULL AND Humidity IS NOT NULL AND MQ9 IS NOT NULL
            AND Time > NOW() - INTERVAL 1 HOUR
            ORDER BY Time DESC
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        data = []
        for row in rows:
            try:
                data.append({
                    'id': int(row['id']),
                    'temperature': float(row['Temperature']),
                    'humidity': float(row['Humidity']),
                    'mq9': float(row['MQ9']),
                    'timestamp': row['Time'].strftime('%Y-%m-%d %H:%M:%S') if row['Time'] else None
                })
            except (ValueError, TypeError):
                continue
        logger.info(f"✓ Extracted {len(data)} records")
        kwargs['ti'].xcom_push(key='sensor_data', value=data)
        return data
    except Error:
        raise
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def predict_mq9(**kwargs):
    logger.info("="*60)
    logger.info("STARTING MQ9 PREDICTION")
    logger.info("="*60)
    sensor_data = kwargs['ti'].xcom_pull(key='sensor_data', task_ids='extract_sensor')
    if not sensor_data:
        kwargs['ti'].xcom_push(key='mq9_predictions', value=[])
        return []
    try:
        model = joblib.load(MODEL_PATH)
        X = pd.DataFrame({
            'Temperature': [d['temperature'] for d in sensor_data],
            'Humidity': [d['humidity'] for d in sensor_data],
            'MQ9_mapped': [d['mq9'] for d in sensor_data],
        })
        predictions = model.predict(X)
        predictions = np.maximum(predictions, 0)
        results = []
        for i, data in enumerate(sensor_data):
            results.append({
                'temperature': data['temperature'],
                'humidity': data['humidity'],
                'mq9_mapped': data['mq9'],
                'predicted_mq9': float(predictions[i]),
                'timestamp': data['timestamp']
            })
        kwargs['ti'].xcom_push(key='mq9_predictions', value=results)
        return results
    except:
        raise

def load_mq9_predictions(**kwargs):
    logger.info("="*60)
    logger.info("LOADING PREDICTIONS TO DATABASE")
    logger.info("="*60)
    predictions = kwargs['ti'].xcom_pull(key='mq9_predictions', task_ids='predict_mq9')
    if not predictions:
        return 0
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        latest_pred = max(predictions, key=lambda x: x['timestamp'])
        query = """
            INSERT INTO mq9_predictions (temperature, humidity, mq9_mapped, predicted, timestamp)
            VALUES (%s,%s,%s,%s,%s)
        """
        cursor.execute(query, (
            latest_pred['temperature'],
            latest_pred['humidity'],
            latest_pred['mq9_mapped'],
            latest_pred['predicted_mq9'],
            latest_pred['timestamp']
        ))
        conn.commit()
        return 1
    except:
        raise
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

default_args = {
    'owner': 'krushaka_vikas',
    'depends_on_past': False,
    'start_date': datetime(2025, 10, 28),
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}
with DAG('mq9_prediction_pipeline', default_args=default_args, schedule='@hourly', catchup=False) as dag:
    t1 = PythonOperator(task_id='extract_sensor', python_callable=extract_sensor_data)
    t2 = PythonOperator(task_id='predict_mq9', python_callable=predict_mq9)
    t3 = PythonOperator(task_id='load_predictions', python_callable=load_mq9_predictions)
    t1 >> t2 >> t3