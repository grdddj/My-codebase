import re
import json
import os
import traceback

from statistics import Statistics
import helpers
from send_mail import send_email
from send_pushbullet import send_pushbullet_message
from config import Config


class NewInLisen:
    def __init__(self):
        self.text_identifier = "brno-lisen"

        file_name = "lisen_seen_flats.json"
        script_directory = os.path.dirname(os.path.realpath(__file__))
        self.file_path = os.path.join(script_directory, file_name)

        self.STATUS_CHANGED = False

        self.already_seen_flats_default = {
            "ids": []
        }
        self.already_seen_flats = {}

    def check_the_flats(self) -> None:
        try:
            self.perform_the_check()
        except Exception as err:
            self.handle_the_unexpected_exception(err)

    def perform_the_check(self) -> None:
        self.create_file_to_store_status_if_it_doesnt_exist()
        self.load_current_status_from_the_file()

        self.load_all_existing_flats()
        self.check_new_flats()

        self.store_the_updated_status_if_it_changed()

    def create_file_to_store_status_if_it_doesnt_exist(self) -> None:
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w") as file:
                json.dump(self.already_seen_flats_default, file, indent=4)

    def load_current_status_from_the_file(self) -> None:
        with open(self.file_path, 'r') as file:
            self.already_seen_flats = json.load(file)

    def load_all_existing_flats(self):
        stats = Statistics()
        self.all_existing_flats = stats._get_results()

    def check_new_flats(self) -> None:
        nonreported_flats = self.get_all_nonreported_flats()

        if len(nonreported_flats) > 0:
            self.STATUS_CHANGED = True
            self.send_new_info_by_mail(nonreported_flats)
            self.include_new_flat_ids_not_to_show_them_again(nonreported_flats)
        else:
            print("NO NEW FLATS FOUND!")

    def get_all_nonreported_flats(self) -> list:
        matching_flats = [flat for flat in self.all_existing_flats
                          if self.matches_the_text_identifier(flat)]
        available_flats = [flat for flat in matching_flats
                           if self.is_still_available(flat)]
        nonreported_flats = [flat for flat in available_flats
                             if not self.was_already_reported(flat)]

        return nonreported_flats

    def matches_the_text_identifier(self, flat: dict) -> bool:
        text_pattern = re.compile(r'{}'.format(self.text_identifier), re.IGNORECASE)
        return bool(text_pattern.search(str(flat)))

    def was_already_reported(self, flat: dict) -> bool:
        return flat["flat_id"] in self.already_seen_flats["ids"]

    @staticmethod
    def is_still_available(flat: dict) -> bool:
        last_update_date = flat["last_update_date"]
        today_date = helpers.get_current_date()
        return last_update_date == today_date

    def include_new_flat_ids_not_to_show_them_again(self, nonreported_flats: list) -> None:
        for flat in nonreported_flats:
            self.already_seen_flats["ids"].append(flat["flat_id"])

    def send_new_info_by_mail(self, nonreported_flats: list) -> None:
        text_to_be_emailed = self.create_text_to_be_emailed(nonreported_flats)

        print(text_to_be_emailed)
        send_email(message_text=text_to_be_emailed, recipients=Config.recipients)

    @staticmethod
    def create_text_to_be_emailed(nonreported_flats: list) -> str:
        text_to_be_emailed = ""
        for flat in nonreported_flats:
            type = flat["type"]
            price = flat["price"]
            link = flat["link"]
            try:
                street = link.split("brno-lisen")[1].split("/")[0].strip("-").capitalize()
            except Exception:
                street = "neznama ulice"
            new_text = f"{type} - {price:,} - {street} - {link}\n"
            text_to_be_emailed += new_text

        return text_to_be_emailed

    def store_the_updated_status_if_it_changed(self) -> None:
        if self.STATUS_CHANGED:
            with open(self.file_path, "w") as file:
                json.dump(self.already_seen_flats, file, indent=4)

    def handle_the_unexpected_exception(self, err):
        print(err)
        title = "NOVE BYTY V LISNI - Unexpected error happened"
        body = f"{err}\n{traceback.format_exc()}"
        send_pushbullet_message(title=title, body=body)


if __name__ == "__main__":
    checker = NewInLisen()
    checker.check_the_flats()
