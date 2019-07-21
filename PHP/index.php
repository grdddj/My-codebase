

<?php
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

?>


<?php
  if (!empty($_GET['act'])) {
    // echo "Hello world 123!"; //Your code here

  } else {
?>
<!-- <form action="script.php" method="get">
  <input type="hidden" name="act" value="run">
  <input type="submit" value="Run me now!">
</form> -->
<p>Do you hate somebody? Do you love somebody? Do you both hate and love somebody? You are on the right address!</p>
<p>Just fill in the forms below, and grant a person with a valuable feedback, they would not get otherwise.</p>

<div  class="collumn" style="float: left; width: 50%;margin-bottom: 25px;">
  <h3>Hate form</h3>
    <form class="quote" name="contactform" method="post" action="script_hate.php">
        <div>
          <label for="hater_name">Your name</label><br>
          <input  name="hater_name" type="text" placeholder="Your name"> <br><br>
        </div>
        <div>
          <label for="other_person_name">Hated person</label><br>
          <input  name="other_person_name" type="text" placeholder="Hated person's name"> <br><br>
        </div>
        <div>
          <label for="reason">Reason you hate him/her</label><br>
          <textarea name="reason" placeholder="Reason" rows="5" cols="40"></textarea>
        </div>
        <br>
        <input type="submit" value="Submit hate!">
    </form>


    <h3>Hate leaderboard</h3>
    <table style="width:100%; text-align: left;">
      <tr>
        <th>Person being hated</th>
        <th>Count of hates</th>
      </tr>

      <?php
        $sql = "SELECT other_person_name, COUNT(other_person_name) as count FROM hates GROUP BY other_person_name ORDER BY 2 DESC";
        $result = $conn->query($sql);
         while ($row = $result->fetch_assoc()) {
    ?>
            <tr>
          <td><?php echo $row['other_person_name']; ?></td>
          <td><?php echo $row['count']; ?></td>
      </tr>

    <?php
         }

      ?>
    </table>

    <h3>Hate details</h3>
    <table style="width:100%; text-align: left;">
      <tr>
        <th>Hater name</th>
        <th>Person being hated</th>
        <th>Reason</th>
      </tr>

      <?php
        $sql = "SELECT * FROM hates ORDER BY hate_id DESC";
        $result = $conn->query($sql);
         while ($row = $result->fetch_assoc()) {
    ?>
            <tr>
          <td><?php echo $row['hater_name']; ?></td>
          <td><?php echo $row['other_person_name']; ?></td>
          <td><?php echo $row['reason']; ?></td>
      </tr>

    <?php
         }

      ?>
    </table>

</div>



<div  class="collumn" style="float: left; width: 50%;margin-bottom: 25px;">
  <h3>Love form</h3>
    <form class="quote" name="contactform" method="post" action="script_love.php">
        <div>
          <label for="lover_name">Your name</label><br>
          <input  name="lover_name" type="text" placeholder="Your name"> <br><br>
        </div>
        <div>
          <label for="other_person_name">Loved person</label><br>
          <input  name="other_person_name" type="text" placeholder="Loved person's name"> <br><br>
        </div>
        <div>
          <label for="reason">Reason you love him/her</label><br>
          <textarea name="reason" placeholder="Reason" rows="5" cols="40"></textarea>
        </div>
        <br>
        <input type="submit" value="Submit love!">
    </form>


    <h3>Love leaderboard</h3>
    <table style="width:100%; text-align: left;">
      <tr>
        <th>Person being loved</th>
        <th>Count of loves</th>
      </tr>

      <?php
        $sql = "SELECT other_person_name, COUNT(other_person_name) as count FROM loves GROUP BY other_person_name ORDER BY 2 DESC";
        $result = $conn->query($sql);
         while ($row = $result->fetch_assoc()) {
    ?>
            <tr>
          <td><?php echo $row['other_person_name']; ?></td>
          <td><?php echo $row['count']; ?></td>
      </tr>

    <?php
         }

      ?>
    </table>

    <h3>Love details</h3>
    <table style="width:100%; text-align: left;">
      <tr>
        <th>Lover name</th>
        <th>Person being loved</th>
        <th>Reason</th>
      </tr>

      <?php
        $sql = "SELECT * FROM loves ORDER BY love_id DESC";
        $result = $conn->query($sql);
         while ($row = $result->fetch_assoc()) {
    ?>
            <tr>
          <td><?php echo $row['lover_name']; ?></td>
          <td><?php echo $row['other_person_name']; ?></td>
          <td><?php echo $row['reason']; ?></td>
      </tr>

    <?php
         }
         $conn->close();

      ?>

    </table>


</div>


<br>
<hr style="clear: both">

<p style="text-align: center;">anITaaJirKa s.r.o., Copyright &copy; 2019</p>

<?php
  }
?>
