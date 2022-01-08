import random
import re
import sys
from typing import Tuple

import fitz

# TODO: create a class

with fitz.open("otazkysrc.pdf") as doc:
    text = ""
    for page in doc:
        text += page.get_text()

part_delimiters = {
    "a": "a) radiokomunikační předpisy:",
    "b": "b) radiokomunikační provoz:",
    "c": "c)  elektrotechnika a radiotechnika:",
    "end": "Vyhodnocení písemné zkoušky ",
}

# Deletes the footer characters
to_remove = re.compile(r"2019_08.*?SRC_2", re.DOTALL)
text = re.sub(to_remove, "", text)

# Optionally dump the text into a file
# with open("text.txt", "w", encoding="utf-8") as f:
#     f.write(text)

QUESTIONS = {
    "a": [],
    "b": [],
    "c": [],
}


def get_q_and_a(buffer: str) -> Tuple[str, str]:
    # TODO: In translation questions, there is a special delimiter "Odpověď:"

    # There is an edge-case when there is no delimiter between question and answer,
    # then we assume the question is on one line and answer is the rest
    if "-" not in buffer:
        lines = buffer.split("\n")
        return lines[0].strip(), " ".join(lines[1:]).strip()

    question_lines = []
    answer_lines = []
    delimiter_found = False
    for part in buffer.split("\n"):
        if not part:
            continue
        part = part.strip()

        # In some rare cases, there is not a dash ("-", ASCII 45) symbol, but
        # end-dash (ASCII 8211)
        if part.startswith("-"):
            delimiter_found = True
            part = part.strip("- ")
        elif ord(part[0]) == 8211:
            part = part[1:]
            delimiter_found = True

        if not delimiter_found:
            question_lines.append(part)
        else:
            answer_lines.append(part)

    return " ".join(question_lines).strip(), " ".join(answer_lines).strip()


question_start = r"^(\d)+\. "

current_part = ""
buffer = ""
for line in text.split("\n")[:]:
    line = line.strip() + "\n"

    # TODO: refactor
    if part_delimiters["a"] in line:
        current_part = "a"
        continue
    elif part_delimiters["b"] in line:
        q_and_a = get_q_and_a(buffer)
        QUESTIONS[current_part].append(q_and_a)
        buffer = ""
        current_part = "b"
        continue
    elif part_delimiters["c"] in line:
        q_and_a = get_q_and_a(buffer)
        QUESTIONS[current_part].append(q_and_a)
        buffer = ""
        current_part = "c"
        continue
    elif part_delimiters["end"] in line:
        q_and_a = get_q_and_a(buffer)
        QUESTIONS[current_part].append(q_and_a)
        break

    if not current_part:
        continue

    # New question starts, evaluate buffer and start buffering new question
    if re.match(question_start, line):
        # In case it is a first question, we do not need to add anything
        # Also ignoring questions with special pattern
        if buffer and "hláskovací abeceda (mezinárodní)" not in buffer:
            q_and_a = get_q_and_a(buffer)
            QUESTIONS[current_part].append(q_and_a)
        buffer = line
        continue

    buffer += line


if __name__ == "__main__":
    while True:
        section = input("Which section (a, b, c)? ")
        if section not in ["a", "b", "c"]:
            print("Only a, b or c are allowed")
            sys.exit(1)

        for q_and_a in random.choices(QUESTIONS[section], k=len(QUESTIONS[section])):
            print(q_and_a[0])
            input("Enter...")
            print(q_and_a[1])
            print(80 * "-")

        print(f"You have finished all the questions in section {section}. Congratulations!")
