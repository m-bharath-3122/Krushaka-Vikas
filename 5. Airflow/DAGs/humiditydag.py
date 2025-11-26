"""
Humidity Prediction from Temperature ETL Pipeline
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

MODEL_PATH = "/opt/airflow/models/humidity_from_temperature_rf_model.joblib" #here replace it with your own path

def extract_temperature_data(**kwargs):
    """
    Extract temperature data from MySQL database (Data_Collection table).
    Uses 'Temperature' and 'Time' columns.
    """
    logger.info("="*60)
    logger.info("STARTING TEMPERATURE DATA EXTRACTION (from Data_Collection)")
    logger.info("="*60)

    connection = None
    try:
        logger.info(f"Connecting to database: {DB_CONFIG['host']}/{DB_CONFIG['database']}")
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT id, Temperature, Time
            FROM Data_Collection 
            WHERE Temperature IS NOT NULL 
                AND Temperature BETWEEN -50 AND 60
                AND Time > NOW() - INTERVAL 1 HOUR
            ORDER BY Time DESC
            LIMIT 100
        """

        cursor.execute(query)
        rows = cursor.fetchall()

        data = []
        for row in rows:
            try:
                # --- Map 'Temperature' to 'temperature' and 'Time' to 'timestamp' ---
                data.append({
                    'id': int(row['id']),
                    'temperature': float(row['Temperature']), 
                    'timestamp': row['Time'].strftime('%Y-%m-%d %H:%M:%S') if row['Time'] else None 
                })
            except (ValueError, TypeError) as e:
                logger.warning(f"Skipping invalid row: {row}, Error: {e}")
                continue
        
        logger.info(f"✓ Successfully extracted {len(data)} temperature records from Data_Collection")
        
        if len(data) > 0:
            temps = [d['temperature'] for d in data]
            logger.info(f"Temperature Statistics:")
            logger.info(f"  - Count: {len(temps)}")
            logger.info(f"  - Mean: {np.mean(temps):.2f}°C")
            logger.info(f"  - Min: {min(temps):.2f}°C")
            logger.info(f"  - Max: {max(temps):.2f}°C")

        kwargs['ti'].xcom_push(key='temperature_data', value=data)
        return data

    except Error as e:
        logger.error(f"✗ Database error during extraction: {e}")
        raise
    except Exception as e:
        logger.error(f"✗ Unexpected error during extraction: {e}")
        raise
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            logger.info("Database connection closed")

def predict_humidity(**kwargs):
    """Load model and predict humidity from temperature"""
    logger.info("="*60)
    logger.info("STARTING HUMIDITY PREDICTION")
    logger.info("="*60)

    temperature_data = kwargs['ti'].xcom_pull(key='temperature_data', task_ids='extract_temperature')

    if not temperature_data or len(temperature_data) == 0:
        logger.warning("⚠ No temperature data available for prediction")
        kwargs['ti'].xcom_push(key='humidity_predictions', value=[])
        return []

    try:
        logger.info(f"Loading model from: {MODEL_PATH}")
        model = joblib.load(MODEL_PATH)
        logger.info("✓ Model loaded successfully")
        logger.info(f"Model type: {type(model).__name__}")

        temperature_values = [item['temperature'] for item in temperature_data]
        X = pd.DataFrame({'Temperature': temperature_values})

        logger.info(f"Input shape: {X.shape}")
        logger.info(f"Temperature range: {X['Temperature'].min():.2f}°C - {X['Temperature'].max():.2f}°C")

        predictions = model.predict(X)
        logger.info("✓ Predictions generated successfully")

        predictions = np.clip(predictions, 0, 100)

        results = []
        for i, item in enumerate(temperature_data):
            results.append({
                'record_id': item['id'],
                'input_temperature': item['temperature'],
                'predicted_humidity': float(predictions[i]),
                'input_timestamp': item['timestamp']
            })

        pred_humidity = [r['predicted_humidity'] for r in results]
        logger.info(f"Prediction Statistics:")
        logger.info(f"  - Count: {len(pred_humidity)}")
        logger.info(f"  - Mean Humidity: {np.mean(pred_humidity):.2f}%")
        logger.info(f"  - Min Humidity: {min(pred_humidity):.2f}%")
        logger.info(f"  - Max Humidity: {max(pred_humidity):.2f}%")

        kwargs['ti'].xcom_push(key='humidity_predictions', value=results)
        return results

    except FileNotFoundError:
        logger.error(f"✗ Model file not found at: {MODEL_PATH}")
        logger.error("  Please ensure 'humidity_from_temperature_model.joblib' is in your 'D:\\airflow\\models' folder.")
        raise
    except Exception as e:
        logger.error(f"✗ Prediction error: {e}")
        raise

def load_humidity_predictions(**kwargs):
    """Store predicted humidity values in MySQL database"""
    logger.info("="*60)
    logger.info("LOADING PREDICTIONS TO DATABASE")
    logger.info("="*60)

    predictions = kwargs['ti'].xcom_pull(key='humidity_predictions', task_ids='predict_humidity')

    if not predictions or len(predictions) == 0:
        logger.warning("⚠ No predictions to load")
        return 0

    connection = None
    try:
        logger.info("Connecting to database for loading predictions")
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        insert_query = """
            INSERT INTO humidity_predictions 
            (input_temperature, predicted_humidity, prediction_timestamp) 
            VALUES (%s, %s, %s)
        """

        insert_data = [
            (
                pred['input_temperature'], 
                pred['predicted_humidity'], 
                pred['input_timestamp']
            ) for pred in predictions
        ]

        cursor.executemany(insert_query, insert_data)
        connection.commit()

        rows_inserted = cursor.rowcount
        logger.info(f"✓ Successfully inserted {rows_inserted} humidity predictions")

        if rows_inserted > 0:
            logger.info("Sample predictions inserted:")
            for i, pred in enumerate(predictions[:3]):
                logger.info(f"  {i+1}. Temp: {pred['input_temperature']:.2f}°C → Humidity: {pred['predicted_humidity']:.2f}%")

        return rows_inserted

    except Error as e:
        logger.error(f"✗ Database error during load: {e}")
        if connection:
            connection.rollback()
            logger.info("Transaction rolled back")
        raise
    except Exception as e:
        logger.error(f"✗ Unexpected error during load: {e}")
        if connection:
            connection.rollback()
        raise
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            logger.info("Database connection closed")

default_args = {
    'owner': 'krushaka_vikas',
    'depends_on_past': False,
    'start_date': datetime(2025, 10, 23),
    'email': ['your_email@example.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'retry_exponential_backoff': True,
    'max_retry_delay': timedelta(minutes=30),
}

dag = DAG(
    dag_id='humidity_prediction_from_temperature',
    default_args=default_args,
    description='ETL pipeline: Predict humidity from temperature using ML model',
    schedule='@hourly',
    catchup=False,
    max_active_runs=1,
    tags=['ml', 'prediction', 'humidity', 'iot', 'krushaka-vikas']
)

extract_task = PythonOperator(
    task_id='extract_temperature',
    python_callable=extract_temperature_data,
    dag=dag,
)

predict_task = PythonOperator(
    task_id='predict_humidity',
    python_callable=predict_humidity,
    dag=dag,
)

load_task = PythonOperator(
    task_id='load_predictions',
    python_callable=load_humidity_predictions,
    dag=dag,
)

extract_task >> predict_task >> load_task