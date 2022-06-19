from pathlib import Path


HERE = Path(__file__).resolve().parent

WORD_FILE = HERE / "wordlists" / "Czech.dic"


def get_default_words() -> set[str]:
    with open(WORD_FILE, "r", encoding="utf-8") as f:
        content = f.readlines()

    return set([word.split("/")[0].strip() for word in content])
