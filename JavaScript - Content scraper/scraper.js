// jQuery is imported in scraper.html, so we can use it

// GLOBAL VARIABLES
var text = "";  // string, storing the whole text
var allWords = []; // array of strings, storing all the separate words
var uniqueWords = []; // array of strings, storing all the unique words
var wordCount = []; // array of integers, storing the occurrences of unique words

var alphabetEng = "abcdefghijklmnopqrstuvwxyz"; // string, english alphabet

// main function that is responsible for getting the data from url
// it also calls other functions that are dependant on these data
function getNewContent() {
  var helper = "https://cors-anywhere.herokuapp.com/"; // string used to enable fetching content from the web with the use of third party server
  var url = $("#url").val(); // getting the url from user

  if(url.includes("http") || url.includes("www")) {
    url = helper + url;
  }

    if (url != "") { // protects from clicking the button without filling url (which would scrap the scrap.html)
        $.ajax({url: url, success: function(result){
            text = extractTextContent(result); // creates a clean text without html tags

            extractWords(text); // creates an array of all separate words
            countWords(allWords); // creates a table of occurences of all unique words
            highestOcurrence(text); // finds out the most common letter
            longestWord(uniqueWords); // finds out the longest unique word
        }});
    }

    else {
      alert("Please fill in the url!"); //prompt user to fill the url input
    }
}

// function used to get rid of html tags and extract clean text
// (parsing the whole html content)
function extractTextContent(content) {
  var span = document.createElement('span');
  span.innerHTML= content;

    var children = span.querySelectorAll('*');
    for(let i = 0 ; i < children.length ; i++) {
        if(children[i].textContent) {
          children[i].textContent+= ' ';
        }

        else {
          children[i].innerText+= ' ';
        }
    }

  return [span.textContent || span.innerText].toString().replace(/ +/g,' ');
};

// function used to fill an array with all separate words (create allWords array)
function extractWords(text) {
  // creating an array of words by splitting the raw text with non-letter characters
   var words = text.split(/[(\s!?*\n:.,/)]+/);
   // loop to transfer all words to lower case, to count them precisely
   // (otherwise "User" in the beginning of the sentence is different as "user" in the middle)
   for (let x = 0; x < words.length; x++) {
     allWords.push(words[x].toLowerCase());
   }
}

// function used to find out the frequency of each word from the list of all words
// it will also create an array of uniqueWords. which will be useful later in longestWord()
function countWords(allWords) {
    // double loop to create an array of unique words together with array of their occurence in text
    for (let i = 0; i < allWords.length; i++) { //going through all the words
        var isThere = false; // boolean to know whether word is already stored in uniqueWords
        for (let j = 0; j < uniqueWords.length; j++) { // identyfying the current word in uniqueWords
            if (allWords[i] == uniqueWords[j]) { // if the word is already in uniqueWords
                isThere = true; // forbid it to be added again
                wordCount[j]++; // increase the number of occurences of a specific word
            }
        }

        if (isThere == false) { // if the word is not in uniqueWords, add it and count his occurrence
            uniqueWords.push(allWords[i]);
            wordCount.push(1);
        }
        isThere = false; //
    }

    // loop to fill the table with all the unique words and their appropriate frequencies
    for (let k = 0; k < uniqueWords.length; k++) {
      $("#occurrenceTable").append("<tr><td>" + uniqueWords[k] + "</td><td>" + wordCount[k] + "</td></tr>");
    }
}

// function used to find the most common letter in the whole text
// if there is more than one most common letter, function will take care of that
function highestOcurrence(text) {
      var alphabet; // string ("array of chars"), all the letters we will search for
      alphabet = alphabetEng; // assigning the English alphabet

      var lettersCount = []; // integer array, to store the counts of all individual letters, to
      var highestOcurrence = 0; // integer, storing the highest frequency of occurrence
      var index = []; // array of integers, storing the indexes of the most frequent letters so far
                  // usually contains one index, but when multiple letters are same frequent, then it will store all indexes
      var amount; // integer, storing the amount of exact letter being processed

      // loop to find out how many times are all letters located in text
      for (let x = 0; x < alphabet.length; x++) {
        var char = alphabet.charAt(x); // getting the letter at exact location in alphabet
        amount = text.split(char).length - 1; // finding out how many times letter is there in the text
        lettersCount.push(amount); // filling the array of counts
      }

      // loop to find out which letter is the most frequent
      for (let y = 0; y < lettersCount.length; y++) {
           var frequency = lettersCount[y]; // finding out specific letter's frequency
            if (frequency > highestOcurrence) { // if there is so far longest word, store it in index
              highestOcurrence = frequency; // update the most frequent amount
              index = []; // make sure there won't be any old indexes from less common letters
              index[0] = y; // store the new most frequent letter's index
            }
            else if (frequency == highestOcurrence) { // if there is other most common letter, also store its index
              index.push(y);
            }
      }

      // if there are more than one most frequent letter, change the grammar from "letter" to "letters"
      if (index.length > 1) {
        $("#letter").html("Most common letters: ");
      }

      // loop to print out the list of the most frequent letter(s)
      for (let z = 0; z < index.length; z++) {
        $("#common").append(alphabet.charAt(index[z]));
        if (z != index.length - 1) {
          $("#common").append(", "); // include commas between all the letters (but not after the last one)
        }
    }
        // print out the frequency of the most common letter(s)
        $("#common").append(" (" + highestOcurrence + " occurrences)");
}

// function used to find out the longest word from the array of unique words
// if there is more than one longest word, function will take care of that
function longestWord(uniqueWords) {

    var longest = 0; // integer, storing the length of longest word so far
    var index = []; // array of integers, storing the indexes of the longest words so far
                // usually contains one index, but when two words have the same length, then it will store both indexes
    var letters; // integer, storing the length of the word being processed

    for (let x = 0; x < uniqueWords.length; x++) {
          letters = uniqueWords[x].length;
            if (letters > longest) { // if there is so far longest word, store it in index
              longest = letters; // update the current highest length
              index = []; // make sure there won't be any old indexes with shorter words
              index[0] = x; // assign the index
            }

            else if (letters == longest) { // if there is other longest word, also store it
              index.push(x);
            }
    }

    // if there is more than one longest word, change the grammar from "word" to "words"
        if (index.length > 1) {
          $("#word").html("Longest words: ");
        }

      // loop to print out the list of the longest word(s)
        for (let y = 0; y < index.length; y++) {
          $("#longest").append(uniqueWords[index[y]]);
          if (y != index.length - 1) {
            $("#longest").append(", "); // include commas between all the words (but not after the last one)
          }
      }
      // print out the length of longest word(s)
          $("#longest").append(" (" + longest + " letters)");
    }


// function used to clear the content before getting a new one
// it allows for repetitive usage of the page without refreshing
function eraseOldContent() {
   text = "";
   allWords = [];
   uniqueWords = [];
   wordCount = [];

   $("#occurrenceTable").html("<tr><th>Word</th><th>Frequency</th></tr>");
   $("#longest").html("");
   $("#common").html("");
   $("#word").html("Longest word: ");
   $("#letter").html("Most common letter: ");
}

// this gets initiated after the page is fully loaded
$(document).ready(function(){
    // click on the button will trigger all the action
    $("button").click(function(){
        eraseOldContent(); // gets rid of old data
        getNewContent(); // fetches new data
        console.log("Thanks for using this service!");
    });
});
