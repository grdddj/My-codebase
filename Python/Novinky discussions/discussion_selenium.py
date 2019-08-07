"""
This script is supposed to fetch comments from articles on the Czech
    news server Novinky.cz, sort them according to their vote points,
    and return the results as a python dictionary, together with 200 response.
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
from bs4 import BeautifulSoup
import time

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
        try:
            discussion_link, article_name = get_main_article_discussion_link_and_article_name()
            error = "Main article supplied."
        except Exception as err:
            print("Unable to extract the link from main article")
            import sys, traceback
            traceback.print_exc(file=sys.stdout)
            return {
                      "article_name": "",
                      "comments": [],
                      "amount": 0,
                      "error": "Unable to extract the link from main article."
                    }

    now =time.time()

    # geckodriver = '/var/www/geckodriver'
    geckodriver = 'D:\\geckodriver.exe'


    # Setting to only wait at most 2 seconds for the html content
    options = webdriver.FirefoxOptions()
    options.set_preference("http.response.timeout", 3)
    options.set_preference("dom.max_script_run_time", 3)
    options.add_argument('-headless')

    driver = webdriver.Firefox(executable_path=geckodriver, options=options)
    print(time.time() - now)

    print(discussion_link)
    driver.get(discussion_link)

    print(time.time() - now)

    driver.implicitly_wait(1)


    count = 0
    while True:
        try:
            print(time.time() - now)
            count +=1
            print(count)
            next_button = driver.find_element_by_class_name("g_f9")
            next_button.click()
        except:
            break

    time.sleep(0.5)
    soup = BeautifulSoup(driver.page_source, "html.parser")

    driver.quit() 

    # Continuing, only when we have acquired valid discussion link
    comments = []

    article_name = "article_name"

    contributions = soup.findAll("div", class_="f_eS")
    print(len(contributions))


    # Processing the comments, extracting its votes and content
    #   and saving them to a local variable
    for comment in contributions:
        try:
            votes_evaluation = comment.find("div", class_="f_eK").findAll("span")
            plus_votes = int(votes_evaluation[0].get_text())
            minus_votes = abs(int(votes_evaluation[-1].get_text()))
        except Exception as err:
            print("unable to locate votes")
            continue

        content = comment.find("div", class_="f_be").get_text().strip()

        comments.append({
            "content": content,
            "plus": plus_votes,
            "minus": minus_votes
        })

    best_or_worst = "best"
    limit = 10
    error = ""

    # Sorting the comments according to the amount of plus points or the time,
    #   according the the supplied parameter
    if best_or_worst == "best":
        comments.sort(reverse=True, key=lambda x:x["plus"])
    elif best_or_worst == "worst":
        comments.sort(reverse=True, key=lambda x:x["minus"])
    elif best_or_worst == "oldest":
        comments.reverse()
    elif best_or_worst == "newest":
        pass


    result = {
              "article_name": article_name,
              "comments": comments[0:limit],
              "amount": len(comments),
              "error": error
            }

    print(result)
    return result

def get_discussion_link_and_article_name(news_link):
    """
    Getting the link to the discussion from the news article
    """
    response = requests.get(news_link)
    soup = BeautifulSoup(response.text, "html.parser")
    discussion_link = soup.find(class_="g_f3").find("a")["href"]

    article_name = soup.find(class_="g_f-").find("h1").get_text().strip()

    print(discussion_link)
    return discussion_link, article_name


def get_main_article_discussion_link_and_article_name():
    """
    Getting the link to the discussion of the main Novinky.cz article
    """
    response = requests.get("https://www.novinky.cz/")
    soup = BeautifulSoup(response.text, "html.parser")

    article_link = soup.find(class_="g_gP").find("li").find("a")["href"]

    print(article_link)

    discussion_link, article_name = get_discussion_link_and_article_name(article_link)

    return discussion_link, article_name


if __name__ == "__main__":
    fetch_comments(news_link="https://www.novinky.cz/zahranicni/evropa/clanek/velky-rusky-dron-kategorie-stealth-ma-za-sebou-prvni-let-40292460")
