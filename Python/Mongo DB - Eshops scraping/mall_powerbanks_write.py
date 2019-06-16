import pymongo
import requests
import json
from bs4 import BeautifulSoup
from datetime import datetime
import re
import math

# Connection to the DB
myclient = pymongo.MongoClient("mongodb+srv://grdddj:myFirstDB@cluster-l467y.mongodb.net/test?retryWrites=true")
mydb = myclient["Mall"]
mycol = mydb["Powerbanks"]

domain = "https://www.mall.cz"
eshop_suffix = " - Mall.cz";

today = datetime.now().strftime('%d-%m-%Y')

count_alltogether = 0
count_one_page = 0
number_of_pages = 0

# Preparing the for loop - finding out how much goods are there and how much at each page
# Try it 5 times as it can sometimes fail with no reason
for x in range(5):
    try:
        page = "https://www.mall.cz/power-bank?page=1"
        response = requests.get(page)
        soup = BeautifulSoup(response.text, "html.parser")
        count_alltogether = int(soup.find("div", {"class": "number-of-products"}))
        count_one_page = len(soup.find("section", {"class": "product-list"}).findAll("article"))
        number_of_pages = math.ceil(count_alltogether / count_one_page)
        message = """There is {} elements alltogether, {} on each page, therefore we will explore {} pages
                    """.format(str(count_alltogether), str(count_one_page), str(number_of_pages))
        print(message)
        break
    except Exception as e:
        print(e)
        print("Something went wrong with the initialisation ({})".format(x))

# Loop through the general supply pages
for page_number in range(2, 1 + number_of_pages):
    # Extracting the page with all the goods
    # Try it 5 times as it can sometimes fail with no reason
    for x in range(5):
        try:
            # Link to the page with a lot of goods
            page = "https://www.mall.cz/power-bank?page=" + str(page_number)

            response = requests.get(page)
            soup = BeautifulSoup(response.text, "html.parser")

            # Getting the array of single items in the page
            all_goods = soup.find("section", {"class": "product-list"}).findAll("article")
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
        except:
            continue

        name = price = capacity = price_10000_mAh = ""
        usb_c = False

        try:
            name = soup.find("h1", {"itemprop": "name"}).get_text().strip()
            price = soup.find("b", {"class": "pro-price"}).get_text().strip()
        except:
            pass

        # Getting all the text descriptions, to extract information from that
        try:
            parameters = soup.find("", {"id": "product-detail-parameters"})
            description = soup.find("", {"id": "product-detail-description"})
            short_description = soup.find("", {"class": "pro-description--short"})
        except:
            pass

        # Finding out whether USB-C is supported
        try:
            text = parameters.get_text().strip() + description.get_text().strip() + short_description.get_text().strip()
            if re.search("USB(| |-| Typ- )C", text) is not None:
                usb_c = True
        except:
            pass

        # Finding the capacity
        for parameter in parameters.findAll("tr"):
            try:
                if parameter.find("th").get_text().strip().startswith("Kapacita"):
                    capacity = parameter.find("td").get_text().strip()
            except:
                pass

        # Transforming the fields
        try:
            capacity = int(capacity[0:capacity.index("mAh")].replace('\xa0',' ').replace(" ", ""))
        except Exception as e:
            print(e)

        try:
            price = int(price[0:price.index("K")].replace('\xa0',' ').replace(" ", ""))
        except Exception as e:
            print(e)

        # Calculating the price of 10000 mAh
        try:
            price_10000_mAh = int(price * 10000 / capacity)
        except:
            pass

        try:
            newItem = {
                "_id": name + eshop_suffix,
                "name": name,
                "price": price,
                "capacity": capacity,
                "usb_c": usb_c,
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
