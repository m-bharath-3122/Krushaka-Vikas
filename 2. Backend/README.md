#  Step 2: Backend API for Sensor Data

This folder contains the server-side PHP code that receives sensor readings from the ESP32 device and stores them in a MySQL database.

## 🧠 What This Code Does

- Listens for HTTP GET requests from the ESP32 (e.g., temperature, humidity, gas levels, etc.)
- Parses the incoming values from URL parameters
- Inserts the data into the appropriate table in the MySQL database

## 📁 Files in This Folder

`data.php` - Handles the incoming HTTP GET requests         
`Krushaka vikas schema.sql` - SQL file to create all the required tables     

## 🛠️ Setup Instructions

1. **Create the MySQL Database**
   - Open your MySQL CLI or phpMyAdmin
   - Run the SQL schema file:
     ```bash
     mysql -u root -p < "Krushaka vikas schema.sql"
     ```

2. **Configure the API Script**
   - Place the `data.php` file inside your web server directory 
   - Edit the database credentials in `data.php`:
     ```php
    // This script receives sensor data from ESP32 using an HTTP GET request
    // It extracts the values from the URL and inserts them into a MySQL database
    // The ESP32 sends requests like: http://your-server-ip/data.php?sensor1=val1&sensor2=val2.
     $servername = "localhost";
     $username = "your_db_user";
     $password = "your_db_password";
     $dbname = "krushaka_vikas";
     ```

3. **Verify the API Endpoint**
   Make sure the ESP32 sends data to the correct endpoint:
   ```
   http://<your-server-ip>/data.php
   ```