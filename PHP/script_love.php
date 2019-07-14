<?php
    function died($error) {
        // your error code can go here
        // echo "We are very sorry, but there were error(s) found with the form you submitted. ";
        // echo "These errors appear below.<br /><br />";
        echo $error."<br /><br />";
        echo "Please go back and fix these errors.<br /><br />";
        die();
    }

    // validation expected data exists
    if($_POST['lover_name'] == "" ||
        $_POST['other_person_name'] == "" ||
        $_POST['reason'] == "") {
          died('You did not specify all the needed parameters - all fields must be filled!');
    }

    $servername = "89.221.219.124";
    $username = "user";
    $password = "password";
    $dbname = "hateyou";

    // Create connection
    $conn = mysqli_connect($servername, $username, $password, $dbname);

    // Check connection
    if (!$conn) {
        die("Connection failed: " . mysqli_connect_error());
    }
    // echo "Connected successfully";

    $stmt = $conn->prepare("INSERT INTO loves (lover_name, other_person_name, reason) VALUES (?, ?, ?)");
    $stmt->bind_param("sss", $lover_name, $other_person_name, $reason);

    $lover_name = $_POST['lover_name']; // required
    $other_person_name = $_POST['other_person_name']; // required
    $reason = $_POST['reason']; // required
    $stmt->execute();

    // $sql = "INSERT INTO hates (lover_name, other_person_name, reason) VALUES ($lover_name, $other_person_name, $reason)";
    //
    //   if ($conn->query($sql) === TRUE) {
    //       echo "New record created successfully";
    //   } else {
    //       echo "Error: " . $sql . "<br>" . $conn->error;
    //   }

    $stmt->close();
    $conn->close();


?>

<!-- include your own success html here -->

Thank you for loving somebody! To see refreshed results, please go back and refresh the page using Ctrl+F5.
