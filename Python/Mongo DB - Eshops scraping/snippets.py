# Including new field - "price_10000_mAh"
for item in db:
    try:
        price = item["price"]
        capacity = item["capacity"]

        price_10000_mAh = int(price * 10000 / capacity)

        myquery = {"_id": item["_id"]}
        newvalues = {"$set": {"price_10000_mAh": price_10000_mAh}}

        mycol.update_one(myquery, newvalues)
        print("Successfully updated: " + item["name"])
    except:
        print("Impossible to update: " + item["name"])


# Deleting entries that do not have a integer in price (have "399,-" there)
my_query = {"price": {"$regex": "-"}}

x = mycol.delete_many(my_query)

#  Adding new value (usb_c)
try:
    myquery = {"_id": newItem["_id"]}
    newvalues = {"$set": {"usb_c": usb_c}}

    mycol.update_one(myquery, newvalues)
    print("Updated: " + newItem["name"] + ", USB-C: " + str(usb_c))
except:
    print("Problems arised: " + newItem["name"])
