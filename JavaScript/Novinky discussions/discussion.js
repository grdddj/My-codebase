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

// Connecting the submit button with the functionality of retrieving and showing data
document.getElementById("submit_button").addEventListener("click", async function() {
  try {
    // Showing the information that we are processing the request
    document.getElementById("error").innerHTML = "Prosím čekejte, Váš požadavek se zpracovává."
    document.getElementById("error").classList.remove("hidden")

    // Hiding the content not to confuse user
    document.getElementById("article_name").classList.add("hidden")
    document.getElementById("amount").classList.add("hidden")
    document.getElementById("content").classList.add("hidden")

    // Preparing the table header, to recreate the table with every new result
    const table_header = `<tr>
                            <th>Komentář</th>
                            <th>Plus</th>
                            <th>Minus</th>
                          </tr>`

    // Crating the data payload we are sending to API
    const payload = {
      news_link: document.getElementById("news_link").value,
      limit: document.getElementById("limit").value,
      best_or_worst: document.getElementById("ordering").value
    }

    console.log("payload", payload)

    // Sending the request and processing the response
    const response = await post_function("http://grdddj.eu:5002/novinky", payload);
    console.log("response", response)
    const content = await response.json()

    console.log("content", content)

    // Showing the name of the article
    document.getElementById("article_name").innerHTML = "Název článku: <b>" + content.article_name + "<b>"

    // Showing the overall amount of comments in the article
    document.getElementById("amount").innerHTML = "Článek obsahuje celkem " + content.amount + " komentářů."

    // Rendering the fetched comments into the table, with their vote-counts
    document.getElementById("content").innerHTML = table_header
    content.comments.forEach(row => {
      document.getElementById("content").innerHTML += "<tr><td>" + row.content + "</td><td>" + row.plus + "</td><td>"+ row.minus + "</td></tr>";
    })

    // Show the content to the user
    document.getElementById("article_name").classList.remove("hidden")
    document.getElementById("amount").classList.remove("hidden")
    document.getElementById("content").classList.remove("hidden")

    // Looking if there is some error message
    const error_message = content.error

    // If everything reached here, hide the error/info message
    if (error_message === "") {
      document.getElementById("error").classList.add("hidden")
    } else if (error_message === "Main article supplied.") {
      document.getElementById("error").innerHTML = "Váš odkaz nerozpoznán, zobrazeny komentáře z hlavního článku."
    } else {
      document.getElementById("error").innerHTML = "Došlo k neočekávané chybě, omlouváme se. Zkuste prosím službu později."
    }
  } catch(err) {
    document.getElementById("error").innerHTML = "Došlo k neočekávané chybě, omlouváme se. Zkuste prosím službu později."
  }
});
