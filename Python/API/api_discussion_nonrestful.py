import requests

from bs4 import BeautifulSoup
from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route("/", methods=["POST"])
def get_comments():

    request_date = request.json["fff"]
    print(request_date)

    ROOT = "https://www.novinky.cz/"

    news_link = "https://www.novinky.cz/krimi/512198-pri-hromadne-nehode-na-kutnohorsku-zemreli-muz-zena-a-dite.html"

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
            plus_votes = int(
                votes_evaluation[-2].get_text()
            )  # ("+2" will get parsed to 2)
            minus_votes = abs(
                int(votes_evaluation[-1].get_text())
            )  # we want the positive number from negative

            content = comment.find("div", class_="content").get_text().strip()

            comments.append(
                {"content": content, "plus": plus_votes, "minus": minus_votes}
            )

    print("Amount of comments:", len(comments))

    # Sorting the comments according to the amount of plus points
    comments.sort(reverse=True, key=lambda x: x["plus"])

    return jsonify(comments)


if __name__ == "__main__":
    app.run(port="5002", debug=True)
