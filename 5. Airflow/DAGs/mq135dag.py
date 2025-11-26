"""
Total_Flow Prediction from IoT Sensors ETL Pipeline
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

MODEL_PATH = "/opt/airflow/models/co2_forecast_model.joblib"

def extract_sensor_data(**kwargs):
    """
    Extract ONLY NEW/RECENT sensor data from MySQL database.
    Extracts data from last 1 hour (adjustable).
    """
    logger.info("="*60)
    logger.info("STARTING SENSOR DATA EXTRACTION (Recent Data Only)")
    logger.info("="*60)

    connection = None
    try:
        logger.info(f"Connecting to database: {DB_CONFIG['host']}/{DB_CONFIG['database']}")
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT id, Temperature, Humidity, MQ135, Time, Total_Flow
            FROM Data_Collection 
            WHERE Temperature IS NOT NULL 
                AND Humidity IS NOT NULL
                AND MQ135 IS NOT NULL
                AND Time > NOW() - INTERVAL 1 HOUR
            ORDER BY Time DESC
        """

        logger.info("Executing query to extract data from last 1 hour...")
        cursor.execute(query)
        rows = cursor.fetchall()

        data = []
        for row in rows:
            try:
                data.append({
                    'id': int(row['id']),
                    'temperature': float(row['Temperature']),
                    'humidity': float(row['Humidity']),
                    'mq135': float(row['MQ135']),
                    'total_flow': float(row['Total_Flow']) if row['Total_Flow'] else None,
                    'timestamp': row['Time'].strftime('%Y-%m-%d %H:%M:%S') if row['Time'] else None
                })
            except (ValueError, TypeError) as e:
                logger.warning(f"Skipping invalid row: {row}, Error: {e}")
                continue
        
        logger.info(f"✓ Successfully extracted {len(data)} sensor records from last 1 hour")
        
        if len(data) > 0:
            logger.info(f"Data Statistics:")
            logger.info(f"  - Temperature: {np.mean([d['temperature'] for d in data]):.2f}°C")
            logger.info(f"  - Humidity: {np.mean([d['humidity'] for d in data]):.2f}%")
            logger.info(f"  - MQ135: {np.mean([d['mq135'] for d in data]):.2f}")
        else:
            logger.warning("⚠ No new data extracted in the last 1 hour")

        kwargs['ti'].xcom_push(key='sensor_data', value=data)
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

def predict_total_flow(**kwargs):
    """Load pre-trained model and predict Total_Flow from sensor data"""
    logger.info("="*60)
    logger.info("STARTING TOTAL_FLOW PREDICTION")
    logger.info("="*60)

    sensor_data = kwargs['ti'].xcom_pull(key='sensor_data', task_ids='extract_sensor')

    if not sensor_data or len(sensor_data) == 0:
        logger.warning("⚠ No sensor data available for prediction")
        kwargs['ti'].xcom_push(key='flow_predictions', value=[])
        return []

    try:
        logger.info(f"Loading model from: {MODEL_PATH}")
        model = joblib.load(MODEL_PATH)
        logger.info("✓ Model loaded successfully")
        logger.info(f"Model type: {type(model).__name__}")

        X = pd.DataFrame({
            'Temperature': [item['temperature'] for item in sensor_data],
            'Humidity': [item['humidity'] for item in sensor_data],
            'MQ135_scaled': [item['mq135'] for item in sensor_data],
            'hour_of_day': [pd.to_datetime(item['timestamp']).hour for item in sensor_data]
        })

        logger.info(f"Input shape: {X.shape}")
        logger.info(f"Feature columns: {list(X.columns)}")

        predictions = model.predict(X)
        logger.info("✓ Predictions generated successfully")

        predictions = np.maximum(predictions, 0)

        results = []
        for i, item in enumerate(sensor_data):
            results.append({
                'temperature': item['temperature'],
                'humidity': item['humidity'],
                'mq135_scaled': item['mq135'],
                'hour_of_day': pd.to_datetime(item['timestamp']).hour,
                'actual_total_flow': item['total_flow'],
                'predicted_total_flow': float(predictions[i]),
                'timestamp': item['timestamp']
            })

        pred_flow = [r['predicted_total_flow'] for r in results]
        logger.info(f"Prediction Statistics:")
        logger.info(f"  - Count: {len(pred_flow)}")
        logger.info(f"  - Mean Predicted Flow: {np.mean(pred_flow):.2f}")
        logger.info(f"  - Min Flow: {min(pred_flow):.2f}")
        logger.info(f"  - Max Flow: {max(pred_flow):.2f}")

        kwargs['ti'].xcom_push(key='flow_predictions', value=results)
        return results

    except FileNotFoundError:
        logger.error(f"✗ Model file not found at: {MODEL_PATH}")
        logger.error("  Please ensure 'linear_regression_model.joblib' is in your models folder.")
        raise
    except Exception as e:
        logger.error(f"✗ Prediction error: {e}")
        raise

def load_flow_predictions(**kwargs):
    """Store predicted Total_Flow values in MySQL database"""
    logger.info("="*60)
    logger.info("LOADING PREDICTIONS TO DATABASE")
    logger.info("="*60)

    predictions = kwargs['ti'].xcom_pull(key='flow_predictions', task_ids='predict_flow')

    if not predictions or len(predictions) == 0:
        logger.warning("⚠ No predictions to load")
        return 0

    connection = None
    try:
        logger.info("Connecting to database for loading predictions")
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()

        insert_query = """
            INSERT INTO model_predictions 
            (temperature, humidity, mq135_scaled, hour_of_day, actual, predicted) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """

        insert_data = [
            (
                pred['temperature'],
                pred['humidity'],
                pred['mq135_scaled'],
                pred['hour_of_day'],
                pred['actual_total_flow'],
                pred['predicted_total_flow']
            ) for pred in predictions
        ]

        cursor.executemany(insert_query, insert_data)
        connection.commit()

        rows_inserted = cursor.rowcount
        logger.info(f"✓ Successfully inserted {rows_inserted} predictions")

        if rows_inserted > 0:
            logger.info("Sample predictions inserted:")
            for i, pred in enumerate(predictions[:3]):
                logger.info(f"  {i+1}. Temp: {pred['temperature']:.2f}°C, Humidity: {pred['humidity']:.2f}%, MQ135_scaled: {pred['mq135_scaled']:.2f}, Hour: {pred['hour_of_day']} → Predicted: {pred['predicted_total_flow']:.2f}, Actual: {pred['actual_total_flow']}")

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
    'start_date': datetime(2025, 10, 28),
    'email': ['your_email@example.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'retry_exponential_backoff': True,
    'max_retry_delay': timedelta(minutes=30),
}

dag = DAG(
    dag_id='total_flow_prediction_pipeline',
    default_args=default_args,
    description='ETL pipeline: Predict Total_Flow from recent sensor data using pre-trained ML model',
    schedule_interval='@hourly',
    catchup=False,
    max_active_runs=1,
    tags=['ml', 'prediction', 'flow', 'iot', 'krushaka-vikas']
)

extract_task = PythonOperator(
    task_id='extract_sensor',
    python_callable=extract_sensor_data,
    dag=dag,
)

predict_task = PythonOperator(
    task_id='predict_flow',
    python_callable=predict_total_flow,
    dag=dag,
)

load_task = PythonOperator(
    task_id='load_predictions',
    python_callable=load_flow_predictions,
    dag=dag,
)
extract_task >> predict_task >> load_task