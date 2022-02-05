import discussion
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_restful import Api, Resource, reqparse

app = Flask(__name__)
api = Api(app)

# Enabling CORS, to use this API everywhere
CORS(app)

# Initializting request parser and adding a key we will be using to transfer data
parser = reqparse.RequestParser()
parser.add_argument("news_link")
parser.add_argument("limit")
parser.add_argument("best_or_worst")


class Novinky_discussion(Resource):
    def post(self):

        # Parsing the parameters and sending them to the function
        request_data = args = parser.parse_args()

        news_link = request_data["news_link"]
        limit = request_data["limit"]
        best_or_worst = request_data["best_or_worst"]

        result = discussion.fetch_comments(news_link, limit, best_or_worst)

        return result


api.add_resource(Novinky_discussion, "/novinky")


if __name__ == "__main__":
    app.run(port="5002", debug=True)
