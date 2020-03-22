"""
This script is supposed to fetch comments from articles on the Czech
    news server Novinky.cz.
"""

import os
import glob
import traceback
import json
import time
import requests
from selenium import webdriver
from bs4 import BeautifulSoup

from element_classes_config import ElementClassesConfig

element_classes = ElementClassesConfig()


def fetch_comments(article_link, folder_name):
    """
    Main function, that is being called from the outside.
    """

    # Checking if the article is not already there from previous pull that
    #   did not completely finish due to some issues
    if article_already_there(article_link, folder_name):
        print("ARTICLE ALREADY THERE")
        return

    # Trying to process the supplied link
    try:
        discussion_link, article_name = get_discussion_link_and_article_name(article_link)
    except Exception as e:
        print(e)
        print(traceback.format_exc())
        print("Unable to locate discussion link")
        return

    article_id = discussion_link.split("/")[-1]
    print("article_id", article_id)
    print("discussion_link", discussion_link)
    print("article_name", article_name)

    now = time.time()

    # Setting to only wait at most 2 seconds for the html content
    options = webdriver.FirefoxOptions()
    options.set_preference("http.response.timeout", 3)
    options.set_preference("dom.max_script_run_time", 3)

    # Determining if we run the script on a laptop or on a server,
    #   and adjusting some important variables
    if os.name == 'posix':
        print("we have linux")
        geckodriver = "/usr/local/bin/geckodriver"
        options.add_argument('-headless')
    else:
        print("I wish we had linux")
        geckodriver = 'D:\\geckodriver.exe'
        options.add_argument('-headless')

    driver = webdriver.Firefox(executable_path=geckodriver, options=options)
    driver.get(discussion_link)
    driver.implicitly_wait(1)

    # Clicking the "Next" button as long it is available to show more comments
    count = 0
    while True:
        try:
            print(time.time() - now)
            count += 1
            print(count)
            next_button_class = element_classes.elements.get("discussions_next_button")
            next_button = driver.find_element_by_class_name(next_button_class)
            next_button.click()
            print("clicking")
        except Exception as err:
            # print(err)
            # print(traceback.format_exc())
            print("breaking the laaaw")
            break

    time.sleep(0.5)
    soup = BeautifulSoup(driver.page_source, "html.parser")

    driver.quit()

    comments = []

    contributions_class = element_classes.elements.get("discussions_contributions")
    contributions = soup.findAll("div", class_=contributions_class)
    print("Number of comments: {}".format(len(contributions)))

    # Processing the comments, extracting its votes and content
    #   and saving them to a local variable
    for comment in contributions:
        try:
            votes_class = element_classes.elements.get("discussions_votes")
            votes_evaluation = comment.find("div", class_=votes_class).findAll("span")
            plus_votes = int(votes_evaluation[0].get_text())
            minus_votes = abs(int(votes_evaluation[-1].get_text()))
        except Exception as err:
            # print(err)
            print("unable to locate votes")
            continue

        content_class = element_classes.elements.get("discussions_content")
        name_class = element_classes.elements.get("discussions_name")

        content = comment.find("div", class_=content_class).get_text().strip()
        name = comment.find("div", class_=name_class).get_text().strip()

        comments.append({
            "name": name,
            "content": content,
            "plus": plus_votes,
            "minus": minus_votes
        })

    # Sorting the comments according to their plus vote number
    comments.sort(key=lambda x: x["plus"], reverse=True)

    result = {
              "article_id": article_id,
              "article_name": article_name,
              "article_link": article_link,
              "comments": comments,
              "amount": len(comments),
            }

    # print(result)
    save_the_results(result, folder_name)

    return result


def get_all_files_with_given_extension(folder, extension):
    """
    Returning all files with a given extension from the same directory as the script
    """

    path_of_the_file = os.path.dirname(os.path.realpath(__file__))
    all_files = glob.glob(os.path.join(path_of_the_file, folder, "*.{}".format(extension)))
    return all_files


def article_already_there(article_link, folder_name):
    """
    Checks if there is already an article processed, so that we are not
        processing it again
    """

    all_files = get_all_files_with_given_extension(folder_name, "json")
    all_file_names = [os.path.splitext(os.path.basename(file))[0] for file in all_files]

    article_id = article_link[-8:]

    return article_id in all_file_names


def save_the_results(results, folder_name):
    """
    Saving the results into a JSON file, with the name corresponding to
        the article ID
    """

    # folder_name = "Fifth_try"
    file_name = "{}.json".format(results["article_id"])
    file_path = os.path.join(folder_name, file_name)

    with open(file_path, "w") as results_file:
        json.dump(results, results_file)


def get_discussion_link_and_article_name(article_link):
    """
    Getting the link to the discussion from the news article
    """
    response = requests.get(article_link)
    soup = BeautifulSoup(response.text, "html.parser")

    discussion_class = element_classes.elements.get("article_discussion")
    article_name_class = element_classes.elements.get("article_name")

    discussion_link = soup.find(class_=discussion_class).find("a")["href"]
    article_name = soup.find(class_=article_name_class).find("h1").get_text().strip()

    return discussion_link, article_name


def article_is_not_old(article_name):
    article_id = int(article_name[-8:])
    return article_id > 40316320


def fetch_comments_for_all_articles_from_file_into_a_folder(file_path, folder_name):
    # Getting all the articles from a file
    with open(file_path, "r") as links_file:
        all_articles = json.load(links_file)

    # creating the folder if it does not exist already
    if not os.path.isdir(folder_name):
        os.mkdir(folder_name)

    index = 0
    for article in all_articles:
        index += 1
        print(80*"*")
        print("{} / {}".format(index, len(all_articles)))
        print(article)
        fetch_comments(article_link=article, folder_name=folder_name)


if __name__ == "__main__":
    file_path = "all_links4.json"
    folder_name = "Fifth_try"
    fetch_comments_for_all_articles_from_file_into_a_folder(file_path, folder_name)
