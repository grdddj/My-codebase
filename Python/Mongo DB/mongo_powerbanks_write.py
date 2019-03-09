import pymongo
import requests
import json
from bs4 import BeautifulSoup

# Connection to the DB
myclient = pymongo.MongoClient("mongodb+srv://grdddj:myFirstDB@cluster-l467y.mongodb.net/test?retryWrites=true")
mydb = myclient["Alza"]
mycol = mydb["Powerbanks"]

# Loop through the general supply pages
for number in range(1, 10):
    # Link to the page with a lot of goods
    page = "https://www.alza.cz/powerbanky/18854166-p" + str(number) + ".htm"

    response = requests.get(page)
    soup = BeautifulSoup(response.text, "html.parser")

    # Extracting individual pieces of goods into array
    all_goods = soup.findAll(class_="canBuy")

    # Looping through individual goods and extracting info about it
    # In the end saving the info to DB

    for goods in all_goods:
        # Initializting fields we want
        link = name = price = capacity = width = depth = weight = price_10000_mAh = ""
        usb_c = False

        try:
            link = "https://www.alza.cz" + goods.find("a")["href"]
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

        newItem = {
            "_id": name,
            "name": name,
            "price": price,
            "capacity": capacity,
            "usb_c": usb_c,
            "width": width,
            "length": length,
            "depth": depth,
            "weight": weight,
            "link": link,
            "price_10000_mAh": price_10000_mAh
        }

        # Saving everything to the DB
        try:
            x = mycol.insert_one(newItem)
            print("Added new document: ")
            print(json.dumps(newItem, indent=4))
        except:
            print("Already there: " + newItem["name"])
            try:
                x = mycol.replace_one({"_id": newItem["_id"]}, newItem)
                print("Document replaced")
            except Exception as e:
                print(e)
                print("Impossible to do anything")

        # #  Adding new value (usb_c)
        # try:
        #     myquery = {"_id": newItem["_id"]}
        #     newvalues = {"$set": {"usb_c": usb_c}}
        #
        #     mycol.update_one(myquery, newvalues)
        #     print("Updated: " + newItem["name"] + ", USB-C: " + str(usb_c))
        # except:
        #     print("Problems arised: " + newItem["name"])


            # try:
            #     newItem["_id"] = newItem["_id"] + "b"
            #     x = mycol.insert_one(newItem)
            # except:
            #     pass



# mydict = { "name": "John", "address": "Highway 37" }
#
 # x = mycol.insert_one(newItem)
#
# print(myclient.list_database_names())

# db = []
#
# for detail in mycol.find():
# 	db.append(detail)
#
# print(db)

# myquery = {"name": "John"}
#
# x = mycol.delete_many(myquery)
