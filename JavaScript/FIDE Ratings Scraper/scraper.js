let playersNumbers = [339300, 306576, 345652];
let helper = "https://cors-anywhere.herokuapp.com/";
let fideRatings = "https://ratings.fide.com/card.phtml?event=";

function getChessPlayersELO() {
  let playersObjects = [];

  playersNumbers.forEach(number => {
    let url = helper + fideRatings + number.toString();
    $.ajax({url: url, success: function(result) {
      text = extractTextContent(result).toString();
      text = text.replace(/\s+/g, " ");

      let beforeName = "(jQuery); ";
      let afterName = " FIDE Chess Profile - Players";
      let name = text.slice(text.indexOf(beforeName) + beforeName.length, text.indexOf(afterName)).replace(",", "");

      let beforeElo = "std."
      let eloString = text.slice(text.indexOf(beforeElo) + beforeElo.length)
      let standardElo = eloString.slice(0, 4);
      let rapidElo = eloString.slice(10, 14);
      let blitzElo = eloString.slice(20, 24);

      let overall = Number(standardElo) + Number(rapidElo) + Number(blitzElo);

      $("#occurrenceTable").append("<tr><td>" + name + "</td><td>" + standardElo + "</td><td>" + rapidElo + "</td><td>" + blitzElo + "</td><td>" + overall + "</td></tr>");
    }})
  });
}

// function used to get rid of html tags and extract clean text
// (parsing the whole html content)
function extractTextContent(content) {
  let span = document.createElement('span');
  span.innerHTML= content;

  let children = span.querySelectorAll('*');
  for(let i = 0 ; i < children.length ; i++) {
      if(children[i].textContent) {
        children[i].textContent+= ' ';
      } else {
        children[i].innerText+= ' ';
      }
  }

  return [span.textContent || span.innerText].toString().replace(/ +/g,' ');
};

$(document).ready(function() {
  getChessPlayersELO(playersNumbers);
});
