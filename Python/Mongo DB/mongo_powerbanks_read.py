import pymongo
import requests
import json
from bs4 import BeautifulSoup

# Connection to the DB
myclient = pymongo.MongoClient("mongodb+srv://grdddj:myFirstDB@cluster-l467y.mongodb.net/test?retryWrites=true")
mydb = myclient["myDB"]
mycol = mydb["trial"]



db = []

for detail in mycol.find():
	db.append(detail)

# # Including new field - "price_10000_mAh"
# for item in db:
#     try:
#         price = item["price"]
#         capacity = item["capacity"]
#
#         price_10000_mAh = int(price * 10000 / capacity)
#
#         myquery = {"_id": item["_id"]}
#         newvalues = {"$set": {"price_10000_mAh": price_10000_mAh}}
#
#         mycol.update_one(myquery, newvalues)
#         print("Successfully updated: " + item["name"])
#     except:
#         print("Impossible to update: " + item["name"])


cheapestDB = mycol.find({"price_10000_mAh": {"$exists": 1}, "usb_c": True},).sort("price_10000_mAh").limit(5)

cheapest = []

for entry in cheapestDB:
    cheapest.append(entry)


print(json.dumps(cheapest, indent=4))


# # Deleting entries that do not have a integer in price (have "399,-" there)
# my_query = {"price": {"$regex": "-"}}
#
# x = mycol.delete_many(my_query)
