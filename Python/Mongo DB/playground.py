import requests
from bs4 import BeautifulSoup

page = "https://notebooky.heureka.cz/"

response = requests.get(page)
soup = BeautifulSoup(response.text, "html.parser")

print(soup)
