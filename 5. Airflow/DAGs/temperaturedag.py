"""
Temperature Prediction from Humidity ETL Pipeline
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

MODEL_PATH = "/opt/airflow/models/temperature_from_humidity_rf_model.joblib"

def extract_humidity_data(**kwargs):

    logger.info("="*60)
    logger.info("STARTING HUMIDITY DATA EXTRACTION (from Data_Collection)")
    logger.info("="*60)

    connection = None
    try:
        logger.info(f"Connecting to database: {DB_CONFIG['host']}/{DB_CONFIG['database']}")
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT id, Humidity, Time
            FROM Data_Collection 
            WHERE Humidity IS NOT NULL 
                AND Humidity BETWEEN 0 AND 100
                AND Time > NOW() - INTERVAL 1 HOUR
            ORDER BY Time DESC
            LIMIT 100
        """

        cursor.execute(query)
        rows = cursor.fetchall()

        data = []
        for row in rows:
            try:
                data.append({
                    'id': int(row['id']),
                    'humidity': float(row['Humidity']), 
                    'timestamp': row['Time'].strftime('%Y-%m-%d %H:%M:%S') if row['Time'] else None 
                })
            except (ValueError, TypeError) as e:
                logger.warning(f"Skipping invalid row: {row}, Error: {e}")
                continue
        
        logger.info(f"✓ Successfully extracted {len(data)} humidity records from Data_Collection")
        
        if len(data) > 0:
            humidities = [d['humidity'] for d in data]
            logger.info(f"Humidity Statistics:")
            logger.info(f"  - Count: {len(humidities)}")
            logger.info(f"  - Mean: {np.mean(humidities):.2f}%")
            logger.info(f"  - Min: {min(humidities):.2f}%")
            logger.info(f"  - Max: {max(humidities):.2f}%")

        kwargs['ti'].xcom_push(key='humidity_data', value=data)
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

def predict_temperature(**kwargs):

    logger.info("="*60)
    logger.info("STARTING TEMPERATURE PREDICTION")
    logger.info("="*60)

    humidity_data = kwargs['ti'].xcom_pull(key='humidity_data', task_ids='extract_humidity')

    if not humidity_data or len(humidity_data) == 0:
        logger.warning("⚠ No humidity data available for prediction")
        kwargs['ti'].xcom_push(key='temperature_predictions', value=[])
        return []

    try:
        logger.info(f"Loading model from: {MODEL_PATH}")
        model = joblib.load(MODEL_PATH)
        logger.info("✓ Model loaded successfully")
        logger.info(f"Model type: {type(model).__name__}")

        humidity_values = [item['humidity'] for item in humidity_data]
        X = pd.DataFrame({'Humidity': humidity_values})

        logger.info(f"Input shape: {X.shape}")
        logger.info(f"Humidity range: {X['Humidity'].min():.2f}% - {X['Humidity'].max():.2f}%")

        predictions = model.predict(X)
        logger.info("✓ Predictions generated successfully")

        # Clip temperature predictions to reasonable range (-50°C to 60°C)
        predictions = np.clip(predictions, -50, 60)

        results = []
        for i, item in enumerate(humidity_data):
            results.append({
                'record_id': item['id'],
                'input_humidity': item['humidity'],
                'predicted_temperature': float(predictions[i]),
                'input_timestamp': item['timestamp']
            })

        pred_temps = [r['predicted_temperature'] for r in results]
        logger.info(f"Prediction Statistics:")
        logger.info(f"  - Count: {len(pred_temps)}")
        logger.info(f"  - Mean Temperature: {np.mean(pred_temps):.2f}°C")
        logger.info(f"  - Min Temperature: {min(pred_temps):.2f}°C")
        logger.info(f"  - Max Temperature: {max(pred_temps):.2f}°C")

        kwargs['ti'].xcom_push(key='temperature_predictions', value=results)
        return results

    except FileNotFoundError:
        logger.error(f"✗ Model file not found at: {MODEL_PATH}")
        logger.error("  Please ensure 'temperature_from_humidity_rf_model.joblib' is in your 'D:\\airflow\\models' folder.")
        raise
    except Exception as e:
        logger.error(f"✗ Prediction error: {e}")
        raise

def load_temperature_predictions(**kwargs):

    logger.info("="*60)
    logger.info("LOADING PREDICTIONS TO DATABASE")
    logger.info("="*60)

    predictions = kwargs['ti'].xcom_pull(key='temperature_predictions', task_ids='predict_temperature')

    if not predictions or len(predictions) == 0:
        logger.warning("⚠ No predictions to load")
        return 0

    connection = None
    try:
        logger.info("Connecting to database for loading predictions")
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()

        insert_query = """
            INSERT INTO temperature_predictions 
            (input_humidity, predicted_temperature, prediction_timestamp) 
            VALUES (%s, %s, %s)
        """

        insert_data = [
            (
                pred['input_humidity'], 
                pred['predicted_temperature'], 
                pred['input_timestamp']
            ) for pred in predictions
        ]

        cursor.executemany(insert_query, insert_data)
        connection.commit()

        rows_inserted = cursor.rowcount
        logger.info(f"✓ Successfully inserted {rows_inserted} temperature predictions")

        if rows_inserted > 0:
            logger.info("Sample predictions inserted:")
            for i, pred in enumerate(predictions[:3]):
                logger.info(f"  {i+1}. Humidity: {pred['input_humidity']:.2f}% → Temperature: {pred['predicted_temperature']:.2f}°C")

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
    'start_date': datetime(2025, 10, 27),
    'email': ['your_email@example.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'retry_exponential_backoff': True,
    'max_retry_delay': timedelta(minutes=30),
}

dag = DAG(
    dag_id='temperature_prediction_from_humidity',
    default_args=default_args,
    description='ETL pipeline: Predict temperature from humidity using ML model',
    schedule='@hourly',
    catchup=False,
    max_active_runs=1,
    tags=['ml', 'prediction', 'temperature', 'iot', 'krushaka-vikas']
)

extract_task = PythonOperator(
    task_id='extract_humidity',
    python_callable=extract_humidity_data,
    dag=dag,
)

predict_task = PythonOperator(
    task_id='predict_temperature',
    python_callable=predict_temperature,
    dag=dag,
)

load_task = PythonOperator(
    task_id='load_predictions',
    python_callable=load_temperature_predictions,
    dag=dag,
)
extract_task >> predict_task >> load_task