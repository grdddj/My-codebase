// Defining the maximum number of results, not to overload the browser
const MAX_RESULTS = 500

// Getting all the comments that user has asked for
async function getComments() {
  try {
    // Checking if user is not asking for too much results, which would have
    //   bad consequence both on the server and the browser
    if (parseInt(document.getElementById("limit").value) > MAX_RESULTS) {
      alertText = `Maximální počet výsledků je ${MAX_RESULTS}. Děkujeme za pochopení.`
      alert(alertText)
      document.getElementById("limit").value = MAX_RESULTS
    }

    // Showing the information that we are processing the request
    const pleaseWaitText = "Prosím čekejte, Váš požadavek se zpracovává."
    document.getElementById("error").innerHTML = pleaseWaitText
    document.getElementById("error").classList.remove("hidden")

    // Hiding the content not to confuse user
    document.getElementById("content").classList.add("hidden")

    // Preparing the table header, to recreate the table with every new result
    const table_header = `<tr>
                            <th>Komentář</th>
                            <th>Plus hlasy</th>
                            <th>Minus hlasy</th>
                            <th>Článek</th>
                          </tr>`

    // Crating the data payload we are sending to API
    const payload = {
      amount: document.getElementById("limit").value,
      best_or_worst: document.getElementById("ordering").value,
      article_id: document.getElementById("extent").value === "all" ?
        0 : document.getElementById("articles").value
    }

    // console.log("payload", payload)

    // Sending the request and processing the response
    const commentsGetEndpoint = "http://grdddj.eu:5115/comments"
    const urlParams = new URLSearchParams(Object.entries(payload));
    const response = await fetch(commentsGetEndpoint + "?" + urlParams);
    const content = await response.json()

    // console.log("content", content)

    // Rendering the fetched comments into the table, with their vote-counts
    document.getElementById("content").innerHTML = table_header
    content.forEach(row => {
      // Defines if to show the whole name of the article or not,
      //   depending on whether we show one article or mix of all
      const linkLook = document.getElementById("extent").value === "all" ?
        `${row.article_name} (${row.comment_amount})` : "odkaz"

      // Filling one row of the table
      document.getElementById("content").innerHTML += `<tr>
                                                    <td>${row.content}</td>
                                                    <td>${row.plus}</td>
                                                    <td>${row.minus}</td>
                                                    <td>
                                                      <a href=${row.link} target=”_blank”>
                                                        ${linkLook}
                                                      </a>
                                                    </td>
                                                  </tr>`
    })

    // Show the content to the user and remove the error message
    document.getElementById("content").classList.remove("hidden")
    document.getElementById("error").innerHTML = ""
  } catch(err) {
    // console.log(err)
    document.getElementById("error").innerHTML = "Došlo k neočekávané chybě, omlouváme se. Zkuste prosím službu později, nebo mimo firemní síť."
  }
}

// Function to fill the select element with choices of all available articles
async function loadAllArticles() {
  const link = "http://grdddj.eu:5115/articles"
  const response = await fetch(link);
  const content = await response.json()

  // Showing how many articles we have, as well as telling users to choose
  document.getElementById("articles").innerHTML += `
    <option value=0>Vyberte z nabídky ${content.length} článků</option>`

  // Filling the choice of all articles
  content.forEach(article => {
    document.getElementById("articles").innerHTML += `
      <option value=${article.id}>${article.name} (${article.comment_amount})</option>`
  })
}

// Connecting the user actions with functionality of retrieving and showing data
document.getElementById("submit_button").addEventListener("click", getComments);
document.getElementById("ordering").addEventListener("change", getComments);
document.getElementById("extent").addEventListener("change", getComments);
document.getElementById("articles").addEventListener("change", getCommentsFromChangingArticle);

// Need to make sure there is individual value in the extent selection
function getCommentsFromChangingArticle() {
  document.getElementById("extent").value = "individual"
  getComments()
}

// Initialize the site
loadAllArticles()
getComments()
