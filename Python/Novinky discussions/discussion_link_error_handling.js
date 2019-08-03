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
  // Showing the information we are processing the request
  document.getElementById("error").innerHTML = "Prosím čekejte, Váš požadavek se zpracovává."
  document.getElementById("error").classList.remove("hidden")

  // Hiding the content not to confuse user
  document.getElementById("amount").classList.add("hidden")
  document.getElementById("content").classList.add("hidden")

  // Preparing the table header, to recreate the table with every new result
  const table_header = `<tr>
                          <th>Komentář</th>
                          <th>Plus</th>
                          <th>Minus</th>
                        </tr>`

  // Validating the input, at least a little bit
  const link = document.getElementById("news_link").value
  const novinky_mentions = link.match(/novinky.cz/)

  // When there is no "novinky.cz" string in the link, raise a warning and return
  if (novinky_mentions === null) {
    document.getElementById("error").innerHTML = "ERROR: Prosím zadejte platný odkaz na článek ze serveru Novinky.cz. Jiné servery prozatím nejsou podporovány."
    return;
  }

  // Crating the data payload we are sending to API
  const payload = {
    news_link: link,
    limit: document.getElementById("limit").value,
    best_or_worst: document.getElementById("ordering").value
  }

  // Sending the request and processing the response
  const response = await post_function("http://grdddj.eu:5002/novinky", payload);
  const content = await response.json

  console.log("content", content)

  // Validating the response - if there are no comments, raise a warning and return
  if (content.comments === undefined) {
    document.getElementById("error").innerHTML = "ERROR: Nenalezeny žádné komentáře. Zkontrolujte prosím, že jste zadali platný odkaz na článek"
    return;
  }

  // Showing the overall amount of comments in the article
  document.getElementById("amount").innerHTML = "Článek obsahuje celkem " + content.amount + " komentářů."

  // Rendering the fetched comments into the table, with their vote-counts
  document.getElementById("content").innerHTML = table_header
  content.comments.forEach(row => {
    document.getElementById("content").innerHTML += "<tr><td>" + row.content + "</td><td>" + row.plus + "</td><td>"+ row.minus + "</td></tr>";
  })

  // Show the content to the user
  document.getElementById("amount").classList.remove("hidden")
  document.getElementById("content").classList.remove("hidden")

  // If everything reached here, hide the error/info message
  document.getElementById("error").classList.add("hidden")
});
