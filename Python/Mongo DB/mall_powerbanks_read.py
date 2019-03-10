import pymongo
import requests
import json
from bs4 import BeautifulSoup

# Connection to the DB
myclient = pymongo.MongoClient("mongodb+srv://grdddj:myFirstDB@cluster-l467y.mongodb.net/test?retryWrites=true")
mydb = myclient["Mall"]
mycol = mydb["Powerbanks"]

db = []

for detail in mycol.find():
	db.append(detail)

cheapestDB = mycol.find({"price_10000_mAh": {"$exists": 1}, "usb_c": True},).sort("price_10000_mAh").limit(5)

cheapest = []

for entry in cheapestDB:
    cheapest.append(entry)

print(json.dumps(cheapest, indent=4))
