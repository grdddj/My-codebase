import click

from word_connector import WordConnector
from wordlist import get_default_words


@click.command()
@click.argument("word")
@click.option("-e", "--word-exceptions", multiple=True, help="Word exceptions")
@click.option("-l", "--limit", type=int, help="Limit of individual results")
def main(word: str, word_exceptions: list[str], limit: int | None):
    WordConnector(
        get_default_words(), word_exceptions=word_exceptions, limit=limit
    ).print_words(word)


if __name__ == "__main__":
    main()
