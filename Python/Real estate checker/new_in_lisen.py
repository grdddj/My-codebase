import re
import json
import os
from statistics import Statistics
import helpers
from send_mail import send_email


class NewInLisen:
    def __init__(self):
        stats = Statistics()
        self.results = stats._get_results()

        self.file_name = "lisen_seen_flats.json"
        self.STATUS_CHANGED = False

        self.already_seen_flats_default = {
            "ids": []
        }
        self.already_seen_flats = {}

    def check_the_flats(self):
        self.create_file_to_store_status_if_it_doesnt_exist()
        self.load_current_status_from_the_file()

        self.check_new_flats()

        self.store_the_updated_status_if_it_changed()

    def create_file_to_store_status_if_it_doesnt_exist(self):
        if not os.path.exists(self.file_name):
            with open(self.file_name, "w") as file:
                json.dump(self.already_seen_flats_default, file, indent=4)

    def load_current_status_from_the_file(self):
        with open(self.file_name, 'r') as file:
            self.already_seen_flats = json.load(file)

    def check_new_flats(self):
        text = "brno-lisen"
        text_pattern = re.compile(r'{}'.format(text), re.IGNORECASE)
        matching_results = [result for result in self.results if text_pattern.search(str(result))]

        available_flats = [flat for flat in matching_results if self.is_still_available(flat)]
        nonreported_flats = [flat for flat in available_flats if not self.was_already_reported(flat)]

        for res in nonreported_flats:
            fields_to_show = ["flat_id", "price", "type", "link", "last_update_date", "first_seen_date"]
            for field in fields_to_show:
                print(res.get(field))
            self.already_seen_flats["ids"].append(res["flat_id"])

        if len(nonreported_flats) > 0:
            self.STATUS_CHANGED = True
            self.send_new_info_by_mail(nonreported_flats)

    @staticmethod
    def send_new_info_by_mail(nonreported_flats):
        text = ""
        for flat in nonreported_flats:
            type = flat["type"]
            price = flat["price"]
            link = flat["link"]
            try:
                street = link.split("brno-lisen")[1].split("/")[0].strip("-").capitalize()
            except Exception as err:
                street = "neznama ulice"
            new_text = f"{type} - {price:,} - {street} - {link}\n"
            text += new_text

        print(text)

        send_email(text.encode('utf-8').decode('ascii'))

    def was_already_reported(self, flat: dict) -> bool:
        return flat["flat_id"] in self.already_seen_flats["ids"]

    @staticmethod
    def is_still_available(flat: dict) -> bool:
        last_update_date = flat.get("last_update_date", "")
        today_date = helpers.get_current_date()
        return last_update_date == today_date

    def store_the_updated_status_if_it_changed(self):
        if self.STATUS_CHANGED:
            with open(self.file_name, "w") as file:
                json.dump(self.already_seen_flats, file, indent=4)


if __name__ == "__main__":
    checker = NewInLisen()
    checker.check_the_flats()
