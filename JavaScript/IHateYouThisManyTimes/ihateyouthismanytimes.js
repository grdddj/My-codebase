// Function to send post requests to specific URL with specific data
// WARNING: the headers are necessary, otherwise it does not work
function post_function(url, data) {
  return fetch(
    url,
    {
      headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json'
      },
      method: "POST",
      body: JSON.stringify(data)
    });
}

const hateLeaderboardTable = `
        <tr>
          <th>Person being hated</th>
          <th>Count of hates</th>
        </tr>
`

const loveLeaderboardTable = `
        <tr>
          <th>Person being loved</th>
          <th>Count of loves</th>
        </tr>
`

const hateDetailsTable = `
        <tr>
          <th>Hater name</th>
          <th>Person being hated</th>
          <th>Reason</th>
        </tr>
`

const loveDetailsTable = `
        <tr>
          <th>Lover name</th>
          <th>Person being loved</th>
          <th>Reason</th>
        </tr>
`

async function update_love_details() {
  let response = await fetch("http://grdddj.eu:5003/love");
  content = await response.json();

  document.getElementById("love_details_table").innerHTML = loveDetailsTable

  content.forEach(entry => {
    const row = "<tr><td>" + entry[1] + "</td><td>" + entry[2] + "</td><td>"+ entry[3] + "</td></tr>";
    document.getElementById("love_details_table").innerHTML += row
  })
}

async function update_love_leaderboard() {
  let response = await fetch("http://grdddj.eu:5003/love_leaderboard");
  content = await response.json();

  document.getElementById("love_leaderboard_table").innerHTML = loveLeaderboardTable

  content.forEach(entry => {
    const row = "<tr><td>" + entry[0] + "</td><td>" + entry[1] + "</td></tr>";
    document.getElementById("love_leaderboard_table").innerHTML += row
  })
}

async function update_hate_details() {
  let response = await fetch("http://grdddj.eu:5003/hate");
  content = await response.json();

  document.getElementById("hate_details_table").innerHTML = hateDetailsTable

  content.forEach(entry => {
    const row = "<tr><td>" + entry[1] + "</td><td>" + entry[2] + "</td><td>"+ entry[3] + "</td></tr>";
    document.getElementById("hate_details_table").innerHTML += row
  })
}

async function update_hate_leaderboard() {
  let response = await fetch("http://grdddj.eu:5003/hate_leaderboard");
  content = await response.json();

  document.getElementById("hate_leaderboard_table").innerHTML = hateLeaderboardTable

  content.forEach(entry => {
    const row = "<tr><td>" + entry[0] + "</td><td>" + entry[1] + "</td></tr>";
    document.getElementById("hate_leaderboard_table").innerHTML += row
  })
}

// Connecting the submit button with the functionality of retrieving and showing data
document.getElementById("submit_love").addEventListener("click", async function() {
  // Verifying the input
  const lover_name = document.getElementById("lover_name").value;
  const other_person_name = document.getElementById("love_other_person_name").value;
  const reason = document.getElementById("love_reason").value;

  if (hater_name == "" || other_person_name == "" || reason == "") {
    alert("Please fill in all the fields!");
    return;
  }

  // Creating the data payload we are sending to API
  const payload = {
    lover_name: lover_name,
    other_person_name: other_person_name,
    reason: reason
  }

  // Sending the request and processing the response
  const response = await post_function("http://grdddj.eu:5003/love", payload);
  const content = await response.json()

  if (content != 200) {
    alert("Love was not send, apologize for that!")
  } else {
    document.getElementById("lover_name").value = ""
    document.getElementById("love_other_person_name").value = ""
    document.getElementById("love_reason").value = ""
  }

  update_love_details()
  update_love_leaderboard()
});

// Connecting the submit button with the functionality of retrieving and showing data
document.getElementById("submit_hate").addEventListener("click", async function() {
  // Verifying the input
  const hater_name = document.getElementById("hater_name").value;
  const other_person_name = document.getElementById("hate_other_person_name").value;
  const reason = document.getElementById("hate_reason").value;

  if (hater_name == "" || other_person_name == "" || reason == "") {
    alert("Please fill in all the fields!");
    return;
  }

  // Creating the data payload we are sending to API
  const payload = {
    hater_name: hater_name,
    other_person_name: other_person_name,
    reason: reason
  }

  // Sending the request and processing the response
  const response = await post_function("http://grdddj.eu:5003/hate", payload);
  const content = await response.json()

  if (content != 200) {
    alert("Hate was not send, apologize for that!")
  } else {
    document.getElementById("hater_name").value = ""
    document.getElementById("hate_other_person_name").value = ""
    document.getElementById("hate_reason").value = ""
  }

  update_hate_details()
  update_hate_leaderboard()
});


update_love_details()
update_love_leaderboard()
update_hate_details()
update_hate_leaderboard()
