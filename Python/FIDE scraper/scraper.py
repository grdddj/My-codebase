import requests
from bs4 import BeautifulSoup
from csv import writer

eloNumbers = [339300, 306576, 345652]

info = []


# Array to store all the player's name and ratings
playersInfo = []

# String to allow for sending all the information in easy readable format
playersInfoToPrint = ""

for number in eloNumbers:
	page = "https://ratings.fide.com/card.phtml?event=" + str(number)
	response = requests.get(page)
	soup = BeautifulSoup(response.text, "html.parser")

	name = str(soup.find(class_="contentpaneopen").find("table").find("table").find("tr").findAll("td")[2].get_text())

	eloClassic = int(soup.find(class_="contentpaneopen").find("table").find("table").find("table").findAll("td")[0].get_text()[5:9])
	eloRapid= int(soup.find(class_="contentpaneopen").find("table").find("table").find("table").findAll("td")[1].find("font").get_text())
	eloBlitz = int(soup.find(class_="contentpaneopen").find("table").find("table").find("table").findAll("td")[2].find("font").get_text())

	playersInfo.append([name.replace("\xa0", ""), eloClassic, eloRapid, eloBlitz])
	
print(playersInfo)

# Transforming the array structure into one string, that is convenient to display
for player in playersInfo:
		for info in player:
			playersInfoToPrint = playersInfoToPrint + str(info) + " "
		playersInfoToPrint = playersInfoToPrint + "\n"
	
print(playersInfoToPrint)