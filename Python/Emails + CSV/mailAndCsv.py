import smtplib, ssl
import requests
from bs4 import BeautifulSoup
from csv import writer
from datetime import datetime

# Defining the array of players whose ELO to fetch
eloNumbers = [339300, 306576, 345652]

# Defining date, to include it into name of CSV file, to avoid overwriting
date = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')

# Defining the player object
class Player:
	def __init__(self, name, eloClassic, eloRapid, eloBlitz):
		self.name = name
		self.eloClassic = eloClassic
		self.eloRapid = eloRapid
		self.eloBlitz = eloBlitz

	# Necessary to allow for printing a single object
	def __str__(self):
		return str(self.__class__) + ": " + str(self.__dict__)

# Array to store all the player's objects
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

	playersInfo.append(Player(name.replace("\xa0", ""), eloClassic, eloRapid, eloBlitz))
	
for player in playersInfo:
	print(vars(player))

# Transforming the array structure into one string, that is convenient to display
for player in playersInfo:
	row = []
	for key, value in player.__dict__.items():
		row.append(str(value))
	playersInfoToPrint += ", ".join(row)
	playersInfoToPrint += "\n"

print(playersInfoToPrint)

# Saving the output as an CSV file
with open("elo-" + date + ".csv", "w") as csv_file:
	csv_writer = writer(csv_file)
	headers = ["Name", "Classic", "Rapid", "Blitz"]
	csv_writer.writerow(headers)

	for player in playersInfo:
		playerRow = []
		for key, value in player.__dict__.items():
			playerRow.append(value)
		csv_writer.writerow(playerRow)

# Sending the output as an email
port = 465  # For SSL
smtp_server = "smtp.gmail.com"
sender_email = "scraper006@gmail.com"  # Enter your address
receiver_email = "jiri.musil006@gmail.com"  # Enter receiver address
password = "+Scraper006+"

message = """\
Subject: Elo of chess players

{playersInfo}
""".format(playersInfo=playersInfoToPrint)

context = ssl.create_default_context()

with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, message)
