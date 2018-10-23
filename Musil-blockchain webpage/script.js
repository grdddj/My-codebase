function changeLanguage() {
  var x = document.getElementsByClassName("language_chosen")[0].getAttribute("lang");
  var y = document.getElementsByClassName("language_chosen");
  console.log(x);
  console.log(y.length);
  if (x == "en") {
      for (let i = 0; i < y.length; i++ ) {
        document.getElementsByClassName("language_chosen")[i].setAttribute("lang", "cz");
      }
  }
  else {
    for (let i = 0; i < y.length; i++ ) {
      document.getElementsByClassName("language_chosen")[i].setAttribute("lang", "en");
    }
  }
}


$(document).ready(function(){
  /*$(".language").click(function(){
    changeLanguage();
  });
  */
});
