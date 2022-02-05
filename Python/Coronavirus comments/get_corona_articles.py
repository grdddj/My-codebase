import json
import os
import time

from bs4 import BeautifulSoup
from element_classes_config import ElementClassesConfig
from selenium import webdriver

element_classes = ElementClassesConfig()


def is_a_good_link(link):
    try:
        int(link[-8:])
        return True
    except (ValueError, TypeError):
        return False


def save_links_into_file(file_path, amount_of_next_clicks=20):
    """
    Main function, that is being called from the outside.
    """

    link = "https://www.novinky.cz/zahranicni/koronavirus"

    now = time.time()

    # Setting to only wait at most 2 seconds for the html content
    options = webdriver.FirefoxOptions()
    options.set_preference("http.response.timeout", 3)
    options.set_preference("dom.max_script_run_time", 3)

    # Determining if we run the script on a laptop or on a server,
    #   and adjusting some important variables
    if os.name == "posix":
        print("we have linux")
        geckodriver = "/usr/local/bin/geckodriver"
        options.add_argument("-headless")
    else:
        print("I wish we had linux")
        geckodriver = "D:\\geckodriver.exe"
        # options.add_argument('-headless')

    driver = webdriver.Firefox(executable_path=geckodriver, options=options)
    driver.get(link)
    driver.implicitly_wait(1)

    # Clicking the "Next" button as long it is available to show more comments
    count = 0
    # while True:
    for _ in range(amount_of_next_clicks):
        try:
            time.sleep(3)
            print(time.time() - now)
            count += 1
            print(count)
            next_button_class = element_classes.elements.get("all_articles_next_button")
            next_button = driver.find_element_by_class_name(next_button_class)
            next_button.click()
            print("clicking")
        except Exception as e:
            print(e)
            print("breaking the laaaw")
            break

    time.sleep(2)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    links_class = element_classes.elements.get("all_articles_links")
    links = soup.find(class_=links_class).findAll("a")

    links_hrefs = [link.get("href") for link in links]
    links_hrefs_valid = [link for link in links_hrefs if is_a_good_link(link)]
    print(links_hrefs_valid)
    print(len(links_hrefs_valid))

    with open(file_path, "w") as results_file:
        json.dump(links_hrefs_valid, results_file)


if __name__ == "__main__":
    file_path = "{}.json".format(str(int(time.time())))
    save_links_into_file(file_path)
