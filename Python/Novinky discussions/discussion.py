"""
This script is supposed to fetch comments from articles on the Czech
    news server Novinky.cz, sort them according to their vote points,
    and return the results as a python dictionary, together with 200 response.
"""

import requests

from bs4 import BeautifulSoup


def fetch_comments(news_link="", limit="", best_or_worst=""):
    """
    Main function, that is being called from the outside.

    Parameters:
    news_link (string) ... the link to the article
    limit (int) ... number of wanted results
    best_or_worst (string) ... the sorting of the results
                                ["best", "worst", "oldest", "newest"]
    """
    # Processing the supplied paraketers and in case they are not suitable,
    #   giving them default values
    try:
        limit = int(limit)
    except:
        limit = 10

    possible_settings = ["best", "worst", "oldest", "newest"]
    if best_or_worst not in possible_settings:
        best_or_worst = "best"

    # Initialising the error variable, which will consume all errors
    error = ""

    # Trying to process the supplied link, and if it is not possible,
    #   supply the comments from the main Novinky.cz article
    try:
        discussion_link, article_name = get_discussion_link_and_article_name(news_link)
    except:
        (
            discussion_link,
            article_name,
        ) = get_main_article_discussion_link_and_article_name()
        error = "No discussion found in your article. We supplied you the main Novinky.cz article."

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

        # Processing the comments, extracting its votes and content
        #   and saving them to a local variable
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

    # Sorting the comments according to the amount of plus points or the time,
    #   accordign the the supplied parameter
    if best_or_worst == "best":
        comments.sort(reverse=True, key=lambda x: x["plus"])
    elif best_or_worst == "worst":
        comments.sort(reverse=True, key=lambda x: x["minus"])
    elif best_or_worst == "oldest":
        comments.reverse()
    elif best_or_worst == "newest":
        pass

    result = {
        "article_name": article_name,
        "comments": comments[0:limit],
        "amount": len(comments),
        "error": error,
    }

    return result, 200


def get_discussion_link_and_article_name(news_link):
    """
    Getting the link to the discussion from the news article
    """
    response = requests.get(news_link)
    soup = BeautifulSoup(response.text, "html.parser")

    discussion_link = (
        "https://www.novinky.cz/" + soup.find(id="discussionEntry").find("a")["href"]
    )

    article_name = soup.find("div", id="articleHeaderBig").find("h1").get_text().strip()

    return discussion_link, article_name


def get_main_article_discussion_link_and_article_name():
    """
    Getting the link to the discussion of the main Novinky.cz article
    """
    response = requests.get("https://www.novinky.cz/")
    soup = BeautifulSoup(response.text, "html.parser")

    article_link = soup.find(class_="topArticle").find("a")["href"]

    discussion_link, article_name = get_discussion_link_and_article_name(article_link)

    return discussion_link, article_name


if __name__ == "__main__":
    fetch_comments()
