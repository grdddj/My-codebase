import requests
from bs4 import BeautifulSoup
from csv import writer

eloNumbers = [339300, 306576, 345652]

for number in eloNumbers:

	page = "https://ratings.fide.com/card.phtml?event=" + str(number)

	response = requests.get(page)

	soup = BeautifulSoup(response.text, "html.parser")

	name = soup.find(class_="contentpaneopen").find("table").find("table").find("tr").findAll("td")[2].get_text()

	elo = soup.find(class_="contentpaneopen").find("table").find("table").find("table").get_text().strip().replace("\n\n\n", ", ")

	print(name, elo)
