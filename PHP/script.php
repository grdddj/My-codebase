<?php

$servername = "89.221.219.124";
$username = "user";
$password = "password";
$dbname = "chat";

// Create connection
$conn = mysqli_connect($servername, $username, $password, $dbname);

// Check connection
if (!$conn) {
    die("Connection failed: " . mysqli_connect_error());
}

$sql = "INSERT INTO users (name, mood) VALUES ('John', 'I am having a good time!')";

  if ($conn->query($sql) === TRUE) {
      echo "New record created successfully";
  } else {
      echo "Error: " . $sql . "<br>" . $conn->error;
  }

  echo "<button><a href='http://www.ihateyouthismanytimes.cz'>Go back</a></button>"

$conn->close();


?>
