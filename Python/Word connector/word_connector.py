from __future__ import annotations

import itertools
import random
import json
from fnmatch import fnmatch
from typing import Any, Sequence

WordCombinations = list[tuple[set[str]]]


class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)


def change_sets_into_lists(json_like: Any) -> Any:
    """So that we can send the results via JSON"""
    return json.loads(json.dumps(json_like, cls=SetEncoder))


def get_all_letter_combinations(word: str) -> set[tuple[str, ...]]:
    return {
        _split_word_with_breaks(word, poss_break)
        for poss_break in _get_possible_breaks(len(word) - 1)
    }


def _get_possible_breaks(length: int) -> set[tuple[bool, ...]]:
    # All combinations of True and False to get all the possible
    # splittings of the word
    return {
        combo
        for combo in itertools.product([True, False], repeat=length)
        if not all(boolean is False for boolean in combo)
    }


def _split_word_with_breaks(word: str, breaks: tuple[bool, ...]) -> tuple[str, ...]:
    # Adding breaks/spaces where they should be
    buf = ""
    for index, should_break in enumerate(breaks):
        buf += word[index]
        if should_break:
            buf += " "
    buf += word[-1]
    return tuple(buf.split())


def is_word_in_list(word: str, all_words: set[str]) -> bool:
    return word in all_words


def words_starting_with(
    beginning: str, all_words: set[str], limit: int | None = None
) -> set[str]:
    def is_ok(word: str) -> bool:
        # Protection against "ch"
        if beginning.endswith("c"):
            if word.startswith(f"{beginning}h"):
                return False

        return word.startswith(beginning)

    start_words = {word for word in all_words if is_ok(word)}
    if limit is None or len(start_words) < limit:
        return start_words
    else:
        return set(random.sample(start_words, limit))


def words_ending_with(
    ending: str, all_words: set[str], limit: int | None = None
) -> set[str]:
    def is_ok(word: str) -> bool:
        # Protection against "ch"
        if ending.endswith("h"):
            if word.endswith("ch"):
                return False

        return word.endswith(ending)

    end_words = {word for word in all_words if is_ok(word)}
    if limit is None or len(end_words) < limit:
        return end_words
    else:
        return set(random.sample(end_words, limit))


def remove_unwanted_words(
    all_words: set[str], unwanted_words: Sequence[str]
) -> set[str]:
    for unwanted in unwanted_words:
        # Accounting for unix wildcards
        all_words = {word for word in all_words if not fnmatch(word, unwanted)}
    return all_words


class WordConnector:
    def __init__(
        self,
        all_words: set[str],
        word_exceptions: Sequence[str] | None = None,
        limit: int | None = None,
    ):
        self.all_words = all_words
        self.limit = limit
        # Removing the invalid words, if there
        if word_exceptions is not None:
            self.all_words = remove_unwanted_words(self.all_words, word_exceptions)

    def get_words(
        self,
        word: str,
    ) -> WordCombinations:
        letter_combos = get_all_letter_combinations(word)
        return self._get_all_word_combinations(letter_combos)

    def print_words(self, word: str) -> None:
        words = self.get_words(word)
        self._print_result(words)

    def _get_all_word_combinations(
        self,
        letter_combos: set[tuple[str, ...]],
    ) -> WordCombinations:
        word_combos = []

        for letter_combo in letter_combos:
            if not self._are_all_middle_words_defined(letter_combo):
                continue

            res = []
            for index, sequence in enumerate(letter_combo):
                if index == 0:  # beginning
                    res.append(
                        words_ending_with(sequence, self.all_words, limit=self.limit)
                    )
                elif index == len(letter_combo) - 1:  # end
                    res.append(
                        words_starting_with(sequence, self.all_words, limit=self.limit)
                    )
                else:  # middle
                    res.append({sequence})

            if all(len(item) > 0 for item in res):
                word_combos.append(tuple(res))

        word_combos.sort(key=lambda x: sum(len(item) for item in x))
        return word_combos

    def _are_all_middle_words_defined(
        self,
        letter_combo: tuple[str, ...],
    ) -> bool:
        if len(letter_combo) < 3:
            return True
        else:
            middle_words = letter_combo[1:-1]
            return all(is_word_in_list(word, self.all_words) for word in middle_words)

    @staticmethod
    def _print_result(word_combos: WordCombinations) -> None:
        total_printed = 0
        for combo in word_combos:
            begin = list(combo[0])
            end = list(combo[-1])

            possible_middle = combo[1:-1]
            middle = ""
            if len(possible_middle) > 0:
                middle = " ".join([list(item)[0] for item in possible_middle])
            middle_words = f" {middle} " if middle else " "

            if len(begin) > len(end):
                for end_word in end:
                    start_word = random.choice(begin)
                    print(f"{start_word:>25}{middle_words}{end_word}")
            else:
                for start_word in begin:
                    end_word = random.choice(end)
                    print(f"{start_word:>25}{middle_words}{end_word}")

            print(f"{len(begin)} x {len(end)}")
            total_printed += min(len(begin), len(end))

        print(f"Total: {total_printed}")
