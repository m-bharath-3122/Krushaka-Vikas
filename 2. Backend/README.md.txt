Step 2: Backend API for Sensor Data

This folder handles the server-side code that receives sensor data from the ESP32 device and stores it in a MySQL database.

What This Does:-

 Listens for HTTP GET requests from ESP32 (with sensor readings)
 Parses values like temperature, humidity, gas levels, soil moisture, rainfall, and water flow
 Inserts this data into the appropriate table inside a MySQL database

Files in This Folder:-

'api.php' or 'data.php' - Handles incoming ESP32 data via GET request 
'Krushaka vikas schema.sql' - SQL script to create all necessary tables 

Setup Instructions:-

1. Create MySQL Database
    Launch your MySQL CLI or use phpMyAdmin
    Run the SQL schema file:
     (mysql -u root -p < "Krushaka vikas schema.sql")


2. Configure the API Script
    Make sure 'data.php' is placed in your server's root directory (e.g., 'htdocs/' or 'public_html/')
    Update DB credentials inside the PHP script:
  
     $servername = "localhost";
     $username = "your_db_user";
     $password = "your_db_password";
     $dbname = "krushaka_vikas";
    

3. Verify API Endpoint
    ESP32 should send data to this:
    
     http://<your-server-ip>/data.php
   