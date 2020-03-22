from flask import Flask, request, jsonify
from flask_restful import reqparse, Resource, Api
from flask_cors import CORS

import reader_from_db

app = Flask(__name__)
api = Api(app)

# Enabling CORS, to use this API everywhere
CORS(app)

# Initializting request parser and adding a key we will be using to transfer data
parser = reqparse.RequestParser()
parser.add_argument('amount')
parser.add_argument('best_or_worst')
parser.add_argument('article_id')


class Novinky_comments(Resource):
    def get(self):

        # Parsing the parameters and sending them to the function
        request_data = parser.parse_args()

        amount = request_data.get("amount", 20)
        best_or_worst = request_data.get("best_or_worst", "best")
        article_id = request_data.get("article_id", "")

        result = reader_from_db.get_comments(amount=amount,
                                             best_or_worst=best_or_worst,
                                             article_id=article_id)

        return jsonify(result)


class Novinky_articles(Resource):
    def get(self):
        result = reader_from_db.get_articles()
        return jsonify(result)


api.add_resource(Novinky_articles, '/articles')
api.add_resource(Novinky_comments, '/comments')


if __name__ == '__main__':
    app.run(port='5115', debug=True)
