"""
This script is fetching the signatures of all presidents of USA
and saving them locally in the form of .png files
"""

import urllib.request

import requests

from bs4 import BeautifulSoup

# Initial page, from which we get the list of presidents
page = "https://en.wikipedia.org/wiki/List_of_Presidents_of_the_United_States"

response = requests.get(page)
soup = BeautifulSoup(response.text, "html.parser")

# Extracting the list of all the presidents
all_presidents = soup.find(class_="wikitable").findAll("b")

# Loop through all the president and gather data about him
for president in all_presidents:
    try:
        name = president.find("a").get_text().strip()
        link = "https://en.wikipedia.org" + president.find("a")["href"]

        response = requests.get(link)
        soup = BeautifulSoup(response.text, "html.parser")

        info = soup.find(class_="infobox vcard").findAll("tr")
    except Exception as e:
        print("Impossible to locate info-card: " + name)
        continue

    signature_link = ""

    # Looking for the "Signature" field and retrieving the link to the image
    for row in info:
        try:
            if row.find("th").get_text().strip() == "Signature":
                signature_link = "https:" + row.find("img")["src"]
                break
        except Exception as e:
            continue

    # Increasing the quality of the picture
    signature_link = signature_link.replace("128px", "256px")

    # Saving the picture locally
    try:
        path = "D:\My-codebase\Python\Wikipedia Scraping\Signatures\{}.png".format(name)
        urllib.request.urlretrieve(signature_link, path)
    except Exception as e:
        print(e)
