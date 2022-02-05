import json
import math
from datetime import datetime

import requests

import pymongo
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Connection to the DB
myclient = pymongo.MongoClient(
    "mongodb+srv://grdddj:myFirstDB@cluster-l467y.mongodb.net/test?retryWrites=true"
)
mydb = myclient["Sauto"]
mycol = mydb["JMK_cars"]

today = datetime.now().strftime("%d-%m-%Y")


# geckodriver = 'D:\\geckodriver.exe'
#
# options = webdriver.FirefoxOptions()
# # options.add_argument('-headless')
#
# webpage = "https://www.sauto.cz/osobni/hledani#!category=1&condition=1&condition=2&condition=4&region=14"
# root = "https://www.sauto.cz/"
#
# driver = webdriver.Firefox(executable_path=geckodriver, options=options)
# driver.get(webpage)
#
# # driver.implicitly_wait(5)
#
# soup = BeautifulSoup(driver.page_source, "html.parser")
#
# # car_links = soup.find(id="changingResults").findAll(class_="toDetail")
# car_links = soup.find(id="changingResults").findAll("div", class_="result")
# print(len(car_links))
# for entry in car_links:
#     try:
#         domain_link = entry.find("a").get("href")
#         to_omit_length = len("?goFrom=list")
#         domain_link = domain_link[0:-to_omit_length]
#         full_link = root + domain_link
#         print(full_link)
#     except AttributeError:
#         print("Does not have a link")
#


link = "https://www.sauto.cz/osobni/detail/opel/agila/18314191"

response = requests.get(link)
soup = BeautifulSoup(response.text, "html.parser")

details_table_rows = soup.find("table", id="detailParams").findAll("tr")

price = (
    year_of_manufacture
) = tachometr = fuel = transmission = country_of_origin = power = volume = STK = ""

for detail in details_table_rows:
    try:
        header_name = detail.find("th").get_text()
        if header_name.startswith("Cena"):
            price = detail.find("td").get_text().strip()
        elif header_name.startswith("Rok"):
            year_of_manufacture = detail.find("td").get_text().strip()
        elif header_name.startswith("Tachometr"):
            tachometr = detail.find("td").get_text().strip()
        elif header_name.startswith("Palivo"):
            fuel = detail.find("td").get_text().strip()
        elif header_name.startswith("Převodovka"):
            transmission = detail.find("td").get_text().strip()
        elif header_name.startswith("Země"):
            country_of_origin = detail.find("td").get_text().strip()
        elif header_name.startswith("Výkon"):
            power = detail.find("td").get_text().strip()
        elif header_name.startswith("Objem"):
            volume = detail.find("td").get_text().strip()
        elif header_name.startswith("STK"):
            STK = detail.find("td").get_text().strip()
    except Exception as e:
        print(e)

print("price", price)
print("year_of_manufacture", year_of_manufacture)
print("tachometr", tachometr)
print("fuel", fuel)
print("transmission", transmission)
print("country_of_origin", country_of_origin)
print("power", power)
print("volume", volume)
print("STK", STK)

try:
    newItem = {
        "_id": link,
        "name": name,
        "price": price,
        "year_of_manufacture": year_of_manufacture,
        "tachometr": tachometr,
        "fuel": fuel,
        "transmission": transmission,
        "country_of_origin": country_of_origin,
        "power": power,
        "volume": volume,
        "STK": STK,
        "link": link,
    }
except:
    continue

bulk = mycol.initialize_unordered_bulk_op()
for car in list_of_cars:
    bulk.find({"_id": car["_id"]}).upsert().replace_one(car)
bulk.execute()


# for index in range (5):
#     print(driver.current_url)
#     soup = BeautifulSoup(driver.page_source, "html.parser")
#
#     car_links = soup.find(id="changingResults").findAll(class_="toDetail")
#     print(len(car_links))
#
#
#     next_page = WebDriverWait(driver, 60).until(EC.visibility_of_element_located((By.ID, "nextPage")))
#     next_page.click()


# driver.save_screenshot('D:\\headless_firefox_test.png')
# driver.quit()
