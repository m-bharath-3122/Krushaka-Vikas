<?php
    echo"hello";
    $hostname = "Paste your host IP/Name";
    $username = "Your Username";
    $password = "Your Password";
    $database = "Database Name";

    $param1 = $_GET['Rainval'];
    $param2 = $_GET['Soilval'];
    $param3 = $_GET['MQ135val'];
    $param4 = $_GET['MQ9val'];
    $param5 = $_GET['h'];
    $param6 = $_GET['t'];
    $param7 = $_GET['flowRate'];
     $param8 = $_GET['totalvolume'];
      echo"hello";
    $conn=mysqli_connect($hostname,$username,$password,$database);
      echo"hello";
   
    if ($conn->connect_error) 
    {
        die("Connection failed: " . $conn->connect_error);
         echo"hello";
    }
  echo"hello";
  
    $sql = "INSERT INTO Data_Collection(Rain,soil,MQ135,MQ9,Humidity,Temperature,Water_Flow,Total_Flow)VALUES('$param1', '$param2', '$param3', '$param4', '$param5', '$param6','$param7','$param8')";

if ($conn->query($sql) === TRUE) {
    echo "Data inserted successfully";
} else {
    echo "Error: " . $sql . "<br>" . $conn->error;
}

$conn->close();
?>
