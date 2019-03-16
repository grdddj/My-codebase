import pymongo
import requests
import json
from bs4 import BeautifulSoup
from datetime import datetime
import re
import math





# Connection to the DB
myclient = pymongo.MongoClient(MONGO_CLIENT)
mydb = myclient[DATABASE]
mycol = mydb[COLECTION]

domain = DOMAIN
eshop_suffix = SUFFIX;

today = datetime.now().strftime('%d-%m-%Y')

count_alltogether = 0
count_one_page = 0
number_of_pages = 0

# Preparing the for loop - finding out how much goods are there and how much at each page
# Try it 5 times as it can sometimes fail with no reason
for x in range(5):
    try:
        page = INIT_PAGE
        response = requests.get(page)
        soup = BeautifulSoup(response.text, "html.parser")

        count_alltogether = TOGETHER
        count_one_page = ONE_PAGE
        number_of_pages = math.ceil(count_alltogether / count_one_page)
        message = """There is {} elements alltogether, {} on each page, therefore we will explore {} pages
                    """.format(str(count_alltogether), str(count_one_page), str(number_of_pages))
        print(message)
        break
    except Exception as e:
        print(e)
        print("Something went wrong with the initialisation ({})".format(x))

# Loop through the general supply pages
for page_number in range(1, 1 + number_of_pages):
    # Extracting the page with all the goods
    # Try it 5 times as it can sometimes fail with no reason
    for x in range(5):
        try:
            # Link to the page with a lot of goods
            page = ITERATIVE_PAGE + str(page_number)

            response = requests.get(page)
            soup = BeautifulSoup(response.text, "html.parser")
            # Getting the array of single items in the page
            all_goods = ALL_GOODS
            break
        except Exception as e:
            print(e)
            print("Something went wrong with the initialisation ({})".format(x))
            if x == 4:
                continue

    # Looping through all the items and retrieving information about each one
    for goods in all_goods:
        try:
            link = domain + LINK
            response = requests.get(link)
            soup = BeautifulSoup(response.text, "html.parser")
        except Exception as e:
            print(e)

        name = price = discount = capacity = weight = price_10000_mAh = ""
        usb_c = False

        try:
            name = NAME
            price = PRICE
        except Exception as e:
            print(e)

        try:
            high_price = HIGH_PRICE_PATH
            price = PRICE
        except Exception as e:
            print(e)

        # Getting the parameters, to extract information from that
        try:
            description = DESCRIPTION
            if re.search("(USB-C|Type-C|Type C)", description) is not None:
                usb_c = True
        except Exception as e:
            print(e)

        try:
            parameters = PARAMETERS
            for row in parameters:
                try:
                    if row.find("td", {"class": "ParamItem"}).get_text().strip().startswith("Kapacita"):
                        capacity = row.find("td", {"class": "ParamValue"}).get_text().strip()
                    if row.find("td", {"class": "ParamItem"}).get_text().strip().startswith("Hmotnost"):
                        weight = row.find("td", {"class": "ParamValue"}).get_text().strip()
                except:
                    pass
        except Exception as e:
            print(e)

        # Transforming the fields
        try:
            capacity = int(capacity)
        except Exception as e:
            print(e)

        try:
            price = int(price[0:price.index(",")].replace('Â','').replace("\xa0", "").replace(" ", ""))
        except Exception as e:
            print (price)
            print(e)

        try:
            weight = int(weight[0:weight.index("g")].replace(" ", ""))
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
