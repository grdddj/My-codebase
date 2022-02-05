import json
import os
import urllib.request
from typing import Dict, List

import requests

import helpers
import logger

WORKING_DIRECTORY = os.path.dirname(os.path.realpath(__file__))

images_dir = "images"
images_dir = os.path.join(WORKING_DIRECTORY, images_dir)

results_file = "results.json"
results_file = os.path.join(WORKING_DIRECTORY, results_file)

api_endpoint = "https://www.sreality.cz/api/cs/v2/estates"
user_agent = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    " (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36"
)
request_headers = {"User-Agent": user_agent}


def add_details_to_all_flats() -> None:
    logger.log_info("Starting to adding detail to all flats")

    helpers.make_dir_if_not_exists(images_dir)

    last_results = get_last_results()
    include_new_information(last_results)
    save_updated_results(last_results)


def get_last_results() -> dict:
    try:
        with open(results_file, "r", encoding="utf-8") as my_file:
            return json.load(my_file)
    except FileNotFoundError:
        return {}


def include_new_information(results: Dict[str, dict]) -> None:
    total_count = len(results)
    counter = 0
    logger.log_info("Total amount of flats: {}".format(total_count))
    for flat_id, info_dict in results.items():
        counter += 1
        print(f"{counter}/{total_count}")
        # TODO: look for other errors than keyerror
        # TODO: find out when the flat is no longer there, and somehow flag
        #   it not to fetch it again and again
        try:
            up_to_date_info = get_up_to_date_info(flat_id)
        except KeyError as err:
            logger.log_error(
                "Impossible to get up_to_date info - id: {flat_id}, err: {err}"
            )
            continue
        except json.decoder.JSONDecodeError as err:
            logger.log_exception(err)
            continue

        incorporate_new_info(info_dict, up_to_date_info)


def incorporate_new_info(info_dict: dict, up_to_date_info: Dict[str, dict]) -> None:
    info_dict["last_update_ts"] = helpers.get_current_ts()
    info_dict["last_update_date"] = helpers.get_current_date()

    for new_key, new_info in up_to_date_info.items():
        if new_key not in info_dict:
            logger.log_info(f"Filling new info (id {info_dict['flat_id']}): {new_key}")

            info_dict[new_key] = new_info
        else:
            # TODO: hotfix, do not hardcode it this way
            if new_key == "last_edit":
                info_dict[new_key] = new_info
                continue

            if info_dict[new_key] != new_info:
                logger.log_info(
                    f"Info changed (id {info_dict['flat_id']}): key {new_key} from {info_dict[new_key]} to {new_info}"
                )

                history_key = "{}_history".format(new_key)
                new_obj = {
                    "date": helpers.get_current_date(),
                    "timestamp": helpers.get_current_ts(),
                    new_key: new_info,
                }

                if history_key in info_dict:
                    info_dict[history_key].append(new_obj)
                else:
                    old_obj = {
                        "date": info_dict["first_seen_date"],
                        "timestamp": info_dict["first_seen_ts"],
                        new_key: info_dict[new_key],
                    }
                    info_dict[history_key] = [old_obj, new_obj]

                info_dict[new_key] = new_info


def get_up_to_date_info(flat_id: str) -> dict:
    url = f"{api_endpoint}/{flat_id}"
    response = requests.get(url, headers=request_headers)
    content = response.json()

    handle_image_downloads(flat_id, content)

    description = content["text"]["value"]

    # TODO: add the agent and agency, as it can come in handy when negotiating
    # TODO: do not store "last_edit" history - hardcoded now

    names_and_identifier_to_capture = {
        "price_detail": "Poznámka k ceně",
        "last_edit": "Aktualizace",
        "state_of_offer": "Stav",
        "owning_state": "Vlastnictví",
        "area_in_square_meters": "Užitná plocha",
        "state_of_object": "Stav objektu",
    }

    captured_info = get_captured_info(content, names_and_identifier_to_capture)

    captured_info["description"] = description
    return captured_info


def get_captured_info(content, names_and_identifier_to_capture) -> dict:
    captured_info = {}
    items = content["items"]
    for item in items:
        item_name = item["name"]
        for key, identifier in names_and_identifier_to_capture.items():
            if item_name == identifier:
                captured_info[key] = item["value"]

    return captured_info


def handle_image_downloads(flat_id: str, content) -> None:
    if not images_already_there(flat_id):
        images_links = get_images_links(content)
        save_all_images_from_links(flat_id, images_links)


def save_all_images_from_links(flat_id: str, images_links: List[str]) -> None:
    for index, link in enumerate(images_links):
        picture_name = get_zero_padded_single_digit_jpg(index)
        flat_images_dir = os.path.join(images_dir, flat_id)

        helpers.make_dir_if_not_exists(flat_images_dir)

        full_picture_path = os.path.join(flat_images_dir, picture_name)
        download_picture(link, full_picture_path)


def get_zero_padded_single_digit_jpg(index: int) -> str:
    if index < 9:
        picture_name = f"0{index + 1}.jpg"
    else:
        picture_name = f"{index + 1}.jpg"
    return picture_name


def images_already_there(flat_id: str) -> bool:
    flat_images_dir = os.path.join(images_dir, flat_id)
    dir_exists = os.path.isdir(flat_images_dir)
    return dir_exists


def get_images_links(content: dict) -> List[str]:
    images_links = []
    images = content["_embedded"]["images"]
    for index, image in enumerate(images):
        href = image["_links"]["view"]["href"]
        images_links.append(href)
    return images_links


def download_picture(url: str, full_picture_path: str) -> None:
    logger.log_info(f"Downloading picture - {url}, {full_picture_path}")
    try:
        urllib.request.urlretrieve(url, full_picture_path)
    except Exception as err:
        logger.log_exception(err)


def save_updated_results(results: dict) -> None:
    logger.log_info("Saving updated results - flat_details")
    with open(results_file, "w", encoding="utf-8") as my_file:
        json.dump(results, my_file, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    add_details_to_all_flats()
