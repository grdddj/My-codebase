from flask import Flask, request, jsonify
from flask_restful import reqparse, Resource, Api
import requests
from bs4 import BeautifulSoup
from flask_cors import CORS

app = Flask(__name__)
api = Api(app)
CORS(app)

# Initializting request parser and adding a key we will be using to transfer data
parser = reqparse.RequestParser()
parser.add_argument('news_link')
parser.add_argument('limit')
parser.add_argument('best_or_worst')

class Novinky_discussion(Resource):
    def post(self):

        request_data = args = parser.parse_args()
        news_link = request_data["news_link"]
        try:
            limit = int(request_data["limit"])
        except
            limit = 10
        best_or_worst = request_data["best_or_worst"]

        ROOT = "https://www.novinky.cz/"

        response = requests.get(news_link)
        soup = BeautifulSoup(response.text, "html.parser")

        discussion_link = ROOT + soup.find(id="discussionEntry").find("a")["href"]

        comments = []
        page = 0

        # Analyzing the discussion pages until we come to a page with no comments
        while True:
            page += 1

            current_link = "{}&page={}".format(discussion_link, page)

            response = requests.get(current_link)
            soup = BeautifulSoup(response.text, "html.parser")

            contributions = soup.find("div", id="contributions").findAll("div", "msgBoxOut")

            # When there are no comments on the page, break the loop
            if not contributions:
                break

            # Processing the comments and extracting its votes and content
            for comment in contributions:
                votes_evaluation = comment.find("div", class_="infoDate").findAll("span")
                plus_votes = int(votes_evaluation[-2].get_text()) # ("+2" will get parsed to 2)
                minus_votes = abs(int(votes_evaluation[-1].get_text())) # we want the positive number from negative

                content = comment.find("div", class_="content").get_text().strip()

                comments.append({
                    "content": content,
                    "plus": plus_votes,
                    "minus": minus_votes
                })

        # Sorting the comments according to the amount of plus points
        if best_or_worst == "best":
            comments.sort(reverse=True, key=lambda x:x["plus"])
        elif best_or_worst == "worst":
            comments.sort(reverse=True, key=lambda x:x["minus"])


        return comments[0:limit]

api.add_resource(Novinky_discussion, '/')


if __name__ == '__main__':
     app.run(port='5002', debug=True)
