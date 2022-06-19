import pytest

from word_connector import (
    WordConnector,
    get_all_letter_combinations,
    _get_possible_breaks,
    is_word_in_list,
    _split_word_with_breaks,
    remove_unwanted_words,
    words_ending_with,
    words_starting_with,
)

MOCK_WORDS = {
    "kafe",
    "coca",
    "cola",
    "caj",
    "chaj",
    "holka",
    "ho",
    "janek",
    "jasan",
    "ojka",
    "ah",
    "kruh",
    "vrtoch",
}

RESULT_FROM_MOCK = [
    (
        {"ah"},
        {"ojka"},
    ),
    (
        {"coca", "cola", "holka", "ojka"},
        {"ho"},
        {"janek", "jasan"},
    ),
]

AHOJ_COMBOS = {
    ("a", "h", "o", "j"),
    ("ah", "o", "j"),
    ("aho", "j"),
    ("ah", "oj"),
    ("a", "hoj"),
    ("a", "h", "oj"),
    ("a", "ho", "j"),
}


def test_get_possible_breaks():
    assert _get_possible_breaks(2) == {
        (True, True),
        (False, True),
        (True, False),
    }


def test_split_word_with_breaks():
    assert _split_word_with_breaks("abcd", (True, True, True)) == ("a", "b", "c", "d")
    assert _split_word_with_breaks("abcd", (True, False, True)) == ("a", "bc", "d")


@pytest.mark.parametrize(
    "word,combos",
    [
        (
            "abc",
            {
                ("a", "b", "c"),
                ("ab", "c"),
                ("a", "bc"),
            },
        ),
        (
            "ahoj",
            AHOJ_COMBOS,
        ),
    ],
)
def test_get_all_letter_combinations(word: str, combos: set[str]):
    assert get_all_letter_combinations(word) == combos


def test_get_all_word_combinations():
    assert (
        WordConnector(MOCK_WORDS)._get_all_word_combinations(AHOJ_COMBOS)
        == RESULT_FROM_MOCK
    )


def test_words_from_word():
    assert WordConnector(MOCK_WORDS).get_words("ahoj") == RESULT_FROM_MOCK


def test_is_word_in_list():
    assert is_word_in_list("kafe", MOCK_WORDS) is True
    assert is_word_in_list("nekafe", MOCK_WORDS) is False


def test_words_starting_with():
    assert words_starting_with("ja", MOCK_WORDS) == {"janek", "jasan"}
    assert words_starting_with("ho", MOCK_WORDS) == {"ho", "holka"}
    # no `chaj`
    assert words_starting_with("c", MOCK_WORDS) == {"coca", "cola", "caj"}


def test_words_ending_with():
    assert words_ending_with("j", MOCK_WORDS) == {"caj", "chaj"}
    # no `vrtoch`
    assert words_ending_with("h", MOCK_WORDS) == {"ah", "kruh"}


def test_remove_unwanted_words():
    assert remove_unwanted_words(MOCK_WORDS, ("kafe",)) == MOCK_WORDS - set(("kafe",))
    assert remove_unwanted_words(MOCK_WORDS, ("ho*",)) == MOCK_WORDS - set(
        ("ho", "holka")
    )
    assert remove_unwanted_words(MOCK_WORDS, ("*h",)) == MOCK_WORDS - set(
        ("ah", "kruh", "vrtoch")
    )
