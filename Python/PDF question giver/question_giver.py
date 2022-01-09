import random
import re
import sys
from typing import Tuple

import fitz  # pip install PyMuPDF


class QuestionGiver:
    pdf_file = "otazkysrc.pdf"
    delimiter = "-"

    def __init__(self) -> None:
        self.text = self.load_text_from_pdf()
        # self.save_text_into_file()

        self.QUESTIONS = {
            "a": [],
            "b": [],
            "c": [],
        }

        self.part_delimiters = {
            "a": "a) radiokomunikační předpisy:",
            "b": "b) radiokomunikační provoz:",
            "c": "c)  elektrotechnika a radiotechnika:",
            "end": "Vyhodnocení písemné zkoušky ",
        }

        self.question_substrings_to_skip = [
            "hláskovací abeceda (mezinárodní)",
        ]

    def load_text_from_pdf(self) -> str:
        with fitz.open(self.pdf_file) as doc:
            text = ""
            for page in doc:
                text += page.get_text()

        # Deletes the footer characters
        to_remove = re.compile(r"2019_08.*?SRC_2", re.DOTALL)
        text = re.sub(to_remove, "", text)

        return text

    def save_text_into_file(self) -> None:
        with open("text.txt", "w", encoding="utf-8") as f:
            f.write(self.text)

    def ask_questions(self) -> None:
        self.fill_questions()

        while True:
            print(
                {
                    key: f"{len(value)} questions"
                    for key, value in self.QUESTIONS.items()
                }
            )
            section = input(f"Which section ({', '.join(self.QUESTIONS.keys())})? ")
            if section not in self.QUESTIONS.keys():
                print(f"Only sections {', '.join(self.QUESTIONS.keys())} are allowed")
                sys.exit(1)

            for q_and_a in random.sample(
                self.QUESTIONS[section], k=len(self.QUESTIONS[section])
            ):
                print(q_and_a[0])
                input("Enter...")
                print(q_and_a[1])
                print(80 * "-")

            print(
                f"You have finished all {len(self.QUESTIONS[section])} questions in section {section}. Congratulations!"
            )

    def fill_questions(self) -> None:
        question_start = r"^(\d)+\. "

        current_part = ""
        buffer = ""
        for line in self.text.split("\n"):
            line = line.strip() + "\n"

            # TODO: refactor
            if self.part_delimiters["a"] in line:
                current_part = "a"
                continue
            elif self.part_delimiters["b"] in line:
                q_and_a = self.get_q_and_a(buffer)
                self.QUESTIONS[current_part].append(q_and_a)
                buffer = ""
                current_part = "b"
                continue
            elif self.part_delimiters["c"] in line:
                q_and_a = self.get_q_and_a(buffer)
                self.QUESTIONS[current_part].append(q_and_a)
                buffer = ""
                current_part = "c"
                continue
            elif self.part_delimiters["end"] in line:
                q_and_a = self.get_q_and_a(buffer)
                self.QUESTIONS[current_part].append(q_and_a)
                break

            if not current_part:
                continue

            # New question starts, evaluate buffer and start buffering new question
            if re.match(question_start, line):
                # In case it is a first question, we do not need to add anything
                # Also ignoring questions with special pattern
                if buffer and not any(
                    [substr in buffer for substr in self.question_substrings_to_skip]
                ):
                    q_and_a = self.get_q_and_a(buffer)
                    self.QUESTIONS[current_part].append(q_and_a)
                buffer = line
                continue

            buffer += line

    def get_q_and_a(self, buffer: str) -> Tuple[str, str]:
        # TODO: In translation questions, there is a special delimiter "Odpověď:"

        # In some cases, there is not a dash ("-", ASCII 45) symbol, but
        # end-dash (ASCII 8211) as a delimiter, so unifying it
        buffer = buffer.replace(chr(8211), self.delimiter)

        # There is an edge-case when there is no delimiter between question and answer,
        # then we assume the question is on one line and answer is the rest
        if self.delimiter not in buffer:
            lines = buffer.split("\n")
            return lines[0].strip(), " ".join(lines[1:]).strip()

        question_lines = []
        answer_lines = []
        delimiter_found = False
        for part in buffer.split("\n"):
            if not part:
                continue
            part = part.strip()

            if part.startswith(self.delimiter):
                delimiter_found = True
                part = part.strip(f"{self.delimiter} ")

            if not delimiter_found:
                question_lines.append(part)
            else:
                answer_lines.append(part)

        return " ".join(question_lines).strip(), " ".join(answer_lines).strip()


if __name__ == "__main__":
    QuestionGiver().ask_questions()
