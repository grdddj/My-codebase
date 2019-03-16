import pymongo
import requests
import json
from bs4 import BeautifulSoup
from datetime import datetime
import re
import math

# Connection to the DB
myclient = pymongo.MongoClient("mongodb+srv://grdddj:myFirstDB@cluster-l467y.mongodb.net/test?retryWrites=true")
mydb = myclient["Czc"]
mycol = mydb["Powerbanks"]

domain = "https://www.czc.cz/"
eshop_suffix = " - czc.cz";

today = datetime.now().strftime('%d-%m-%Y')

count_alltogether = 0
count_one_page = 0
number_of_pages = 0

# Preparing the for loop - finding out how much goods are there and how much at each page
# Try it 5 times as it can sometimes fail with no reason
for x in range(5):
    try:
        page = "https://www.czc.cz/powerbanky-baterie-a-nabijecky_3/produkty?q-first=1"
        response = requests.get(page)
        soup = BeautifulSoup(response.text, "html.parser")

        count_alltogether = int(soup.find("", {"class": "order-by-sum"}).get_text()[0:4].strip())
        count_one_page = len(soup.findAll("div", {"class": "new-tile"}))
        number_of_pages = math.ceil(count_alltogether / count_one_page)
        message = """There is {} elements alltogether, {} on each page, therefore we will explore {} pages
                    """.format(str(count_alltogether), str(count_one_page), str(number_of_pages))
        print(message)
        break
    except:
        print("Something went wrong with the initialisation ({})".format(x))

# Loop through the general supply pages
for page_number in range(1, 1 + number_of_pages):
    # Extracting the page with all the goods
    # Try it 5 times as it can sometimes fail with no reason
    number = 1 + 26 * (page_number - 1)
    for x in range(5):
        try:
            # Link to the page with a lot of goods
            page = "https://www.czc.cz/powerbanky-baterie-a-nabijecky_3/produkty?q-first=" + str(number)

            response = requests.get(page)
            soup = BeautifulSoup(response.text, "html.parser")

            # Getting the array of single items in the page
            all_goods = soup.findAll("div", {"class": "new-tile"})
            break
        except:
            print("Something went wrong with the initialisation ({})".format(x))
            if x == 4:
                continue

    # Looping through all the items and retrieving information about each one
    for goods in all_goods:
        try:
            link = domain + goods.find("a")["href"]
            response = requests.get(link)
            soup = BeautifulSoup(response.text, "html.parser")
        except Exception as e:
            print(e)

        name = price = capacity = weight = price_10000_mAh = ""
        usb_c = False

        try:
            name = soup.find("h1").get_text().strip()
            price = soup.find("", {"class": "total-price"}).find("span", {"class": "price-vatin"}).get_text().strip()
        except Exception as e:
            print(e)

        # Getting the parameters, to extract information from that
        try:
            parameters = soup.find("", {"id": "pd-parameter"}).findAll("p")
            for entry in parameters:
                if entry.find("span").get_text().startswith("Kapacita"):
                    capacity = entry.find("strong").get_text().strip().replace(u'\xa0', ' ').replace(" ", "")
                if entry.find("span").get_text().startswith("Hmotnost"):
                    weight = entry.find("strong").get_text().strip().replace(u'\xa0', ' ').replace(" ", "")
        except Exception as e:
            print(e)

        try:
            description = soup.find("", {"class": "pd-description"}).get_text().strip()
            if re.search("(USB-C|Type-C|Type C)", description) is not None:
                usb_c = True
        except Exception as e:
            print(e)

        # Transforming the fields
        try:
            name = name[0:name.index("  ")]
        except Exception as e:
            print(e)

        try:
            capacity = int(capacity)
        except Exception as e:
            print(e)

        try:
            price = int(price[0:price.index("K")].replace('Â','').replace("\xa0", "").replace(" ", ""))
        except Exception as e:
            print (price)
            print(e)

        try:
            weight = int(weight.replace(" ", ""))
        except Exception as e:
            print (weight)
            print(e)

        # Calculating the price of 10000 mAh
        try:
            price_10000_mAh = int(price * 10000 / capacity)
        except Exception as e:
            print(e)

        try:
            newItem = {
                "_id": name + eshop_suffix,
                "name": name,
                "price": price,
                "capacity": capacity,
                "usb_c": usb_c,
                "weight": weight,
                "link": link,
                "last_update": today,
                "price_10000_mAh": price_10000_mAh
            }
        except Exception as e:
            print(e)

        # Saving everything to the DB
        try:
            x = mycol.insert_one(newItem)
            print("Added new document: ")
            print(json.dumps(newItem, indent=4))
        except Exception as e:
            print(e)
