from flask import Flask, jsonify
from flask_cors import CORS
from flask_restful import Api, Resource, reqparse
from flask.wrappers import Response
from flask import request

from functools import lru_cache
from pathlib import Path
import logging
import json

from word_connector import WordConnector, change_sets_into_lists
from wordlist import get_default_words

app = Flask(__name__)
api = Api(app)

CORS(app)

HERE = Path(__file__).resolve().parent
LIKE_FILE = HERE / "likes.json"
LOG_FILE = HERE / "logs.txt"

if not LIKE_FILE.exists():
    with open(LIKE_FILE, "w") as f:
        json.dump({}, f)


logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)


class WordAPI(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("word", type=str, required=True)
        parser.add_argument("limit", type=int, required=False)
        parser.add_argument(
            "word_exceptions", type=str, action="append", required=False
        )
        request_data = parser.parse_args()

        word = request_data["word"]
        limit = request_data["limit"] or 1000
        word_exceptions = tuple(request_data["word_exceptions"] or [])

        logging.info(
            f"IP address: {request.remote_addr}. Word: {word}. Limit: {limit}. Exceptions: {word_exceptions}"
        )

        if not word:
            response = jsonify({"message": "Word is empty"})
            response.status_code = 400
            return response

        return get_json_results(word, word_exceptions, limit)


@lru_cache(maxsize=16)
def get_json_results(word: str, word_exceptions: tuple[str], limit=100) -> Response:

    result = WordConnector(
        get_default_words(), word_exceptions=word_exceptions, limit=limit
    ).get_words(word)

    return jsonify(change_sets_into_lists(result))


class BestAPI(Resource):
    def get(self):
        return jsonify(get_likes())

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("word_combination", type=str, required=True)
        request_data = parser.parse_args()
        word_combination = request_data["word_combination"]

        app.logger.info(f"word_combination: {word_combination}")

        save_word_combination_like(word_combination)

        return jsonify({"message": "Word saved"})


def save_word_combination_like(word_combination: str):
    likes = json.loads(LIKE_FILE.read_text())

    if word_combination not in likes:
        likes[word_combination] = 0
    likes[word_combination] += 1

    with open(LIKE_FILE, "w", encoding="utf-8") as f:
        json.dump(likes, f, indent=4)


def get_likes() -> dict[str, int]:
    return json.loads(LIKE_FILE.read_text())


api.add_resource(WordAPI, "/word")
api.add_resource(BestAPI, "/best")


if __name__ == "__main__":
    app.run(port=5015, debug=True)
