CREATE DATABASE IF NOT EXISTS krushaka_vikas 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE krushaka_vikas;

CREATE TABLE IF NOT EXISTS Data_Collection (
    id INT(11) NOT NULL AUTO_INCREMENT,
    Time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    Rain DOUBLE NOT NULL,
    soil DOUBLE NOT NULL,
    MQ135 DOUBLE NOT NULL,
    MQ9 DOUBLE NOT NULL,
    Humidity DOUBLE NOT NULL,
    Temperature DOUBLE NOT NULL,
    WaterFlow DOUBLE NOT NULL,
    TotalFlow DOUBLE NOT NULL,
    PRIMARY KEY (id),
    INDEX idx_time (Time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS model_predictions (
    id BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT,
    temperature FLOAT DEFAULT NULL,
    humidity FLOAT DEFAULT NULL,
    mq135_scaled FLOAT DEFAULT NULL,
    hour_of_day INT(11) DEFAULT NULL,
    actual FLOAT DEFAULT NULL,
    predicted FLOAT DEFAULT NULL,
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS mq9_predictions (
    id INT(11) NOT NULL AUTO_INCREMENT,
    timestamp DATETIME NOT NULL,
    temperature FLOAT NOT NULL,
    humidity FLOAT NOT NULL,
    mq9_mapped FLOAT NOT NULL,
    actual FLOAT DEFAULT NULL,
    predicted FLOAT NOT NULL,
    created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

CREATE TABLE IF NOT EXISTS temperature_predictions (
    id INT(11) NOT NULL AUTO_INCREMENT,
    input_humidity FLOAT NOT NULL,
    predicted_temperature FLOAT NOT NULL,
    prediction_timestamp TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    INDEX idx_timestamp (prediction_timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS humidity_predictions (
    id INT(11) NOT NULL AUTO_INCREMENT,
    input_temperature FLOAT NOT NULL,
    predicted_humidity FLOAT NOT NULL,
    prediction_timestamp TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    INDEX idx_timestamp (prediction_timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS sensor_data (
    id INT(6) UNSIGNED NOT NULL AUTO_INCREMENT,
    temperature FLOAT NOT NULL,
    humidity FLOAT NOT NULL,
    reading_time TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

SHOW TABLES;