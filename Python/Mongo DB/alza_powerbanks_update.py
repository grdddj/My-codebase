import pymongo
import requests
import json
import math
from bs4 import BeautifulSoup
from datetime import datetime

# Connection to the DB
myclient = pymongo.MongoClient("mongodb+srv://grdddj:myFirstDB@cluster-l467y.mongodb.net/test?retryWrites=true")
mydb = myclient["Alza"]
mycol = mydb["Powerbanks2"]

domain = "https://www.alza.cz"
eshop_suffix = " - Alza.cz";

today = datetime.now().strftime('%Y-%m-%d')

count_alltogether = 0
count_one_page = 0
number_of_pages = 0

# Preparing the for loop - finding out how much goods are there and how much at each page
# Try it 5 times as it can sometimes fail with no reason
for x in range(5):
    try:
        page = "https://www.alza.cz/powerbanky/18854166-p1.htm"
        response = requests.get(page)
        soup = BeautifulSoup(response.text, "html.parser")

        count_alltogether = int(soup.find("span", {"id": "lblNumberItem"}).get_text())
        count_one_page = len(soup.findAll(class_="canBuy"))
        number_of_pages = math.ceil(count_alltogether / count_one_page)
        message = """There is {} elements alltogether, {} on each page, therefore we will explore {} pages
                    """.format(str(count_alltogether), str(count_one_page), str(number_of_pages))
        print(message)
        break
    except Exception as e:
        print(e)
        print("Something went wrong with the initialisation ({})".format(x))

# Loop through the general supply pages
for number in range(1, 1 + number_of_pages):

    for x in range(5):
        try:
            # Link to the page with a lot of goods
            page = "https://www.alza.cz/powerbanky/18854166-p" + str(number) + ".htm"
            response = requests.get(page)
            soup = BeautifulSoup(response.text, "html.parser")

            # Extracting individual pieces of goods into array
            all_goods = soup.findAll(class_="canBuy")
            break
        except:
            print("Something went wrong with the initialisation ({})".format(x))
            if x == 4:
                continue

    # Looping through individual goods and extracting info about it
    # In the end saving the info to DB
    for goods in all_goods:
        # Initializting fields we want
        link = name = price = capacity = width = depth = weight = price_10000_mAh = ""
        usb_c = False

        try:
            link = domain + goods.find("a")["href"]
            response = requests.get(link)
            soup = BeautifulSoup(response.text, "html.parser")
        except:
            continue

        try:
            name = soup.find("h1").get_text().strip()
            price = soup.find(class_="bigPrice").get_text().strip()
        except:
            price = "unknown"

        try:
            goods_details = soup.findAll(class_="row")
        except:
            good_details = []

        # Looping through all the fields in the goods and saving what we want
        for detail in goods_details:
            try:
                if detail.find(class_="typeName").get_text().strip().startswith("Kapacita"):
                    capacity = detail.find(class_="value").get_text().strip()
                if detail.find(class_="typeName").get_text().strip().startswith("Šířka"):
                    width = detail.find(class_="value").get_text().strip()
                if detail.find(class_="typeName").get_text().strip().startswith("Výška"):
                    length = detail.find(class_="value").get_text().strip()
                if detail.find(class_="typeName").get_text().strip().startswith("Hloubka"):
                    depth = detail.find(class_="value").get_text().strip()
                if detail.find(class_="typeName").get_text().strip().startswith("Hmotnost"):
                    weight = detail.find(class_="value").get_text().strip()
                if detail.find(class_="typeName").get_text().strip().startswith("Výstupy"):
                    if detail.find(class_="value").get_text().strip().find("USB-C") != -1:
                        usb_c = True
            except Exception as e:
                pass

        # Processing the info to have consistency (parsing values)
        # Every value is processed in sigle try-statement, not to influence other
        try:
            name = name.replace("\u010dern\u00e1", "")
        except Exception as e:
            print(e)

        try:
            capacity = int(capacity[0:capacity.index("mAh")].replace('\xa0',' ').replace(" ", ""))
        except Exception as e:
            print(e)

        try:
            price = int(price[0:-2].replace('\xa0',' ').replace(" ", ""))
        except Exception as e:
            print(e)

        try:
            width = int(float(width[0:width.index("m")].replace('\xa0',' ').replace(" ", "").replace(",", ".")))
        except Exception as e:
            print(e)

        try:
            length = int(float(length[0:length.index("m")].replace('\xa0',' ').replace(" ", "").replace(",", ".")))
        except Exception as e:
            print(e)

        try:
            depth = int(float(depth[0:depth.index("m")].replace('\xa0',' ').replace(" ", "").replace(",", ".")))
        except Exception as e:
            print(e)

        try:
            weight = int(float(weight[0:weight.index("g")].replace('\xa0',' ').replace(" ", "").replace(",", ".")))
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
                "width": width,
                "length": length,
                "depth": depth,
                "weight": weight,
                "link": link,
                "last_update": today,
                "price_10000_mAh": price_10000_mAh
            }
        except:
            continue

        # Saving everything to the DB
        # If document already exists, just update the prices and last_update day
        try:
            x = mycol.insert_one(newItem)
            print("Added new document: ")
            print(json.dumps(newItem, indent=4))
        except Exception as e:
            try:
                myquery = {"_id": newItem["_id"]}
                newvalues = {"$set": {"price": price, "price_10000_mAh": price_10000_mAh, "last_update": today}}
                mycol.update_one(myquery, newvalues)
                print("Updated: " + newItem["name"])
            except:
                print(e)
