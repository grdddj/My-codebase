WORDS_ENDPOINT = "http://grdddj.eu:5015/word";
BEST_ENDPOINT = "http://grdddj.eu:5015/best";

let WORDS_FROM_API = [];

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
        }
    );
}

async function get_results(word, word_exceptions) {
    console.log(`Searching for word: ${word}`);
    const limit = 100;
    const response = await post_function(WORDS_ENDPOINT, {
        word, word_exceptions, limit
    });
    console.log(response);
    const content = await response.json();
    console.log(content);
    return content;
}

async function show_best_words() {
    $("#loading").attr("hidden", false);
    $("#best_words_results").attr("hidden", true);
    $("#words_results").attr("hidden", true);
    $("#best_words_results_paragraph").empty();
    console.log("Showing best words...");
    let response = await fetch(BEST_ENDPOINT);
    const best_words = await response.json();
    console.log(best_words);
    let best_words_array = [];
    for (const [words, likes] of Object.entries(best_words)) {
        best_words_array.push([words, likes]);
    }
    $("#best_combo_amount").text(best_words_array.length);
    best_words_array.sort((a, b) => b[1] - a[1]);
    for (const [words, likes] of best_words_array) {
        render_word_combination_likes(words, likes);
    }
    $("#best_words_results").attr("hidden", false);
    $("#loading").attr("hidden", true);
}

async function show_words() {
    $("#loading").attr("hidden", false);
    $("#words_results").attr("hidden", true);
    $("#best_words_results").attr("hidden", true);
    const word = $("#word").val().toLowerCase();;
    if (word.length == 0) {
        alert("Slovo nemůže býti prázdné!");
        $("#loading").attr("hidden", true);
        return;
    }
    const word_exceptions = $("#word_exceptions").val().split(/[\s,]/).filter(word => word.length > 0).map(word => word.toLowerCase());
    console.log(word_exceptions);
    $("#ignored_words").text(word_exceptions.join(', '));

    WORDS_FROM_API = await get_results(word, word_exceptions);

    $("#combo_amount").text(get_word_amount(WORDS_FROM_API));
    console.log(`Possible categories: ${WORDS_FROM_API.length}`);
    render_words();
    console.log("Words shown!");
    $("#words_results").attr("hidden", false);
    $("#loading").attr("hidden", true);
}

function render_words() {
    $("#words_results_paragraph").empty();
    console.log(`Possible categories: ${WORDS_FROM_API.length}`);
    for (const word_combination of WORDS_FROM_API) {
        console.log(word_combination.length);

        let begin = word_combination[0];
        let end = word_combination[word_combination.length - 1];

        let possible_middle = word_combination.slice(1, word_combination.length - 1);
        let middle_str = "";
        if (possible_middle.length > 0) {
            let all_middles = [];
            for (const middle of possible_middle) {
                all_middles.push(middle[0]);
            }
            middle_str = all_middles.join(" ");
            middle_str = ` ${middle_str} `;
        } else {
            middle_str = " ";
        }

        if (begin.length > end.length) {
            for (const end_word of end) {
                let start_word = begin[Math.floor(Math.random() * begin.length)];
                const text = `${start_word}${middle_str}${end_word}`;
                render_word_combination(text);
            }
        } else {
            for (const start_word of begin) {
                let end_word = end[Math.floor(Math.random() * end.length)];
                const text = `${start_word}${middle_str}${end_word}`;
                render_word_combination(text);
            }
        }
    }
}

function render_word_combination(word_combination) {
    const button = `<button onclick="send_like('${word_combination}');" class="btn">Like!</button>`
    $("#words_results_paragraph").append(`<p>${word_combination} ${button} </p>`);
}

function render_word_combination_likes(word_combination, like_amount) {
    const button = `<button onclick="send_like('${word_combination}', true);" class="btn">Like!</button>`
    $("#best_words_results_paragraph").append(`<p> ${word_combination} (${like_amount}) ${button} </p>`);
}

function get_word_amount(api_result) {
    let word_amount = 0;
    for (const group of api_result) {
        word_amount += Math.min(group[0].length, group[group.length - 1].length);
    }
    return word_amount;
}

async function send_like(word_combination, refresh_best_words = false) {
    console.log(`Sending like for: ${word_combination} `);
    await post_function(BEST_ENDPOINT, {
        word_combination
    });
    console.log(`${word_combination} got like`);
    if (refresh_best_words) {
        setTimeout(show_best_words, 300);
    }
}


$(document).ready(function () {
    $("#show_words").click(function () {
        console.log("Clicked ukaz!");
        show_words();
    });
    $("#show_best").click(function () {
        console.log("Clicked best!");
        show_best_words();
    });
    $("#randomize_words").click(function () {
        console.log("Clicked randomized!");
        render_words();
    });
});
