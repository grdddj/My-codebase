// window.post = function(url, data) {
//   return fetch(url, {method: "POST", body: JSON.stringify(data)});
// }
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

document.getElementById("submit_button").addEventListener("click", async function(){
  payload = {
    news_link: document.getElementById("text_input").value,
    limit: "5",
    best_or_worst: "best"
    }
  let response = await post_function("http://grdddj.eu:5002/", payload);

  content = await response.json();
  console.log(content);

  content.forEach(row => {
    document.getElementById("demo").innerHTML += row.content + "<br>";
  })
});
