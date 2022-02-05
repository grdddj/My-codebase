import json
import os
import re
import shutil

import requests

import helpers
import logger

WORKING_DIRECTORY = os.path.dirname(os.path.realpath(__file__))

results_file = "results.json"
results_file = os.path.join(WORKING_DIRECTORY, results_file)

backup_dir = "backups"
backup_dir = os.path.join(WORKING_DIRECTORY, backup_dir)

api_endpoint = "https://www.sreality.cz/api/cs/v2/estates"
user_agent = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    " (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36"
)
request_headers = {"User-Agent": user_agent}

one_page_limit = 999

# TODO: create some aggregator CLI script that will have some
#   functions data results available and input() will choose which one to show
# average price on a certain day
# histogram of prices at a certain day
# average cost for a square meter

# TODO: create Django app to show these statistics and overall data (images etc.)
# OR creating a PyQt5 frontend

# TODO: add Mongo DB instead of JSON files

# TODO: include more stuff in helpers

# TODO: refactor as much more as possible

# TODO: think about all function and variable names

# TODO: think about the environmental variables (results_file is common)

# TODO: incorporate error handling into the network part and parsing part

# TODO: create some appropriate comments

# TODO: consider creating classes and objects, not having to pass so many
#   variables around

# TODO: could add some basic testing, at least mypy tests with typing

# TODO: think about the .format() strings and maybe replace them with f-strings


def fetch_and_update_all_new_flats():
    logger.log_info("Starting to fetch and update all flats")

    helpers.make_dir_if_not_exists(backup_dir)

    archive_last_results()

    content = get_content()
    analyze_content(content)


def get_content():
    number_of_results = get_number_of_results()
    logger.log_info(f"Number of results: {number_of_results}")

    number_of_pages = get_number_of_pages(number_of_results, one_page_limit)
    results_per_page = number_of_results // number_of_pages
    estates = []
    for page_num in range(1, number_of_pages + 1):
        new_estates = get_new_estates(page_num, results_per_page)
        estates.extend(new_estates)

    logger.log_info(f"Number of fetched results: {len(estates)}")
    return estates


def get_number_of_results():
    # Testing request to get the amount of results
    test_url = (
        f"{api_endpoint}?category_main_cb=1&category_type_cb=1"
        "&locality_region_id=14&per_page=10&sort=1"
    )
    test_response = requests.get(test_url, headers=request_headers)
    test_response_obj = test_response.json()
    number_of_results = test_response_obj["result_size"]

    return number_of_results


def get_number_of_pages(number_of_results, one_page_limit):
    for i in range(1, 1000):
        if number_of_results // i <= one_page_limit:
            return i
    return 1


def get_new_estates(page_num, results_per_page):
    url = (
        f"{api_endpoint}?category_main_cb=1&category_type_cb=1"
        f"&locality_region_id=14&page={page_num}&per_page={results_per_page}&sort=1"
    )
    response = requests.get(url, headers=request_headers)
    response_obj = response.json()
    new_estates = response_obj["_embedded"]["estates"]
    return new_estates


def analyze_content(estates):
    flat_dict = get_flat_dict(estates)

    last_results = get_last_results()

    # TODO: create a function for this - probably reuse the single flat one
    for flat_id, info in flat_dict.items():
        if flat_id not in last_results:
            logger.log_info(f"Adding new flat: id {flat_id}")

            info["first_seen_ts"] = info["last_update_ts"]
            info["first_seen_date"] = info["last_update_date"]
            last_results[flat_id] = info
        else:
            last_results[flat_id]["last_update_ts"] = info["last_update_ts"]
            last_results[flat_id]["last_update_date"] = info["last_update_date"]
            if info["price"] != last_results[flat_id]["price"]:
                logger.log_info(
                    f"Price changed (id {flat_id}):from {last_results[flat_id]['price']} to {info['price']}"
                )

                new_price_obj = {
                    "date": info["last_update_date"],
                    "timestamp": info["last_update_ts"],
                    "price": info["price"],
                }

                if "price_history" in last_results[flat_id]:
                    last_results[flat_id]["price_history"].append(new_price_obj)
                else:
                    old_price_obj = {
                        "date": last_results[flat_id]["first_seen_date"],
                        "timestamp": last_results[flat_id]["first_seen_ts"],
                        "price": last_results[flat_id]["price"],
                    }
                    last_results[flat_id]["price_history"] = [
                        old_price_obj,
                        new_price_obj,
                    ]

                last_results[flat_id]["price"] = info["price"]

    save_new_results(last_results)


def get_flat_dict(estates):
    update_ts = helpers.get_current_ts()
    update_date = helpers.get_current_date()

    flat_dict = {}
    for flat in estates:
        locality_criptic = flat["seo"]["locality"]
        locality = flat["locality"]
        flat_id = str(flat["hash_id"])
        price = flat["price"]
        name = flat["name"]

        type = get_type_from_name(name)

        link = f"https://www.sreality.cz/detail/prodej/byt/{type}/{locality_criptic}/{flat_id}"

        obj_to_save = {
            "flat_id": flat_id,
            "link": link,
            "price": price,
            "locality": locality,
            "type": type,
            "name": name,
            "last_update_ts": update_ts,
            "last_update_date": update_date,
        }
        flat_dict[flat_id] = obj_to_save

    return flat_dict


def get_type_from_name(name):
    # Targets 1+1, 2+kk and similar paterns
    pattern = r"\b(\d+\+\S+)\b"
    try:
        type = re.findall(pattern, name)[0]
    except IndexError:
        type = "Unknown"
    return type


def save_new_results(flat_dict):
    logger.log_info("Saving new results - all_flats")
    with open(results_file, "w", encoding="utf-8") as my_file:
        json.dump(flat_dict, my_file, indent=4, ensure_ascii=False)


def get_last_results():
    try:
        with open(results_file, "r", encoding="utf-8") as my_file:
            results = json.load(my_file)
            return results
    except FileNotFoundError:
        return {}


def archive_last_results():
    now_ts = helpers.get_current_ts()
    backup_name = f"results_backup_{now_ts}.json"
    backup_path = os.path.join(backup_dir, backup_name)

    logger.log_info(f"Backing up results - {backup_path}")

    try:
        shutil.copyfile(results_file, backup_path)
    except FileNotFoundError as err:
        logger.log_exception(err)


if __name__ == "__main__":
    fetch_and_update_all_new_flats()
