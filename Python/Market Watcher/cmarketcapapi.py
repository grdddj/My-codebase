import json
import os
import traceback

import requests
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects

from config import Config


class CMarketCapWatcher:
    def __init__(self) -> None:
        self.url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
        self.parameters = {"start": "1", "limit": "20", "convert": "USD"}
        headers = {
            "Accepts": "application/json",
            "X-CMC_PRO_API_KEY": Config.coinmarketcap_api_token,
        }

        self.session = requests.Session()
        self.session.headers.update(headers)

        self.price_levels_and_steps_default = {
            "Bitcoin": {"price_level": 55000, "step": 5000},
            "Ethereum": {"price_level": 2000, "step": 500},
            "Litecoin": {"price_level": 200, "step": 50},
        }

        self.price_levels_and_steps = {}
        self.STATUS_CHANGED = False

        file_name = "price_levels.json"
        script_directory = os.path.dirname(os.path.realpath(__file__))
        self.file_path = os.path.join(script_directory, file_name)

    def check_the_situation(self) -> None:
        try:
            self.prepare_and_perform_the_check()
        except Exception as err:
            self.handle_the_unexpected_exception(err)

    def prepare_and_perform_the_check(self) -> None:
        self.create_file_to_store_status_if_it_doesnt_exist()
        self.load_current_status_from_the_file()

        self.get_and_process_the_api_data()

        if self.STATUS_CHANGED:
            self.store_the_updated_status()

    def create_file_to_store_status_if_it_doesnt_exist(self) -> None:
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w") as file:
                json.dump(self.price_levels_and_steps_default, file, indent=4)

    def load_current_status_from_the_file(self) -> None:
        with open(self.file_path, "r") as file:
            self.price_levels_and_steps = json.load(file)

    def get_and_process_the_api_data(self) -> None:
        data = self.get_data_from_api()
        self.process_data(data)

    def store_the_updated_status(self):
        with open(self.file_path, "w") as file:
            json.dump(self.price_levels_and_steps, file, indent=4)

    def get_data_from_api(self) -> dict:
        try:
            response = self.session.get(self.url, params=self.parameters)
            return json.loads(response.text)
        except (ConnectionError, Timeout, TooManyRedirects) as e:
            print(e)
            return {}

    def process_data(self, data: dict) -> None:
        asset_list = data["data"]
        for asset in asset_list:
            self.check_asset(asset)

    def check_asset(self, asset: dict) -> None:
        name = asset["name"]
        if name in self.price_levels_and_steps:
            price = int(asset["quote"]["USD"]["price"])
            limit_price = self.price_levels_and_steps[name]["price_level"]
            if price > limit_price:
                self.STATUS_CHANGED = True
                title = "The price has been reached!"
                message = f"{name} has risen over {limit_price} - it is {price}"
                self.send_pushbullet_message(title=title, body=message)
                print(message)
                step = self.price_levels_and_steps[name]["step"]
                self.price_levels_and_steps[name]["price_level"] += step
            else:
                message = f"Price of {name} is {price}. Still lower than the limit of {limit_price}"
                print(message)

    @staticmethod
    def send_pushbullet_message(title: str, body: str) -> None:
        msg = {"type": "note", "title": title, "body": body}
        resp = requests.post(
            "https://api.pushbullet.com/v2/pushes",
            data=json.dumps(msg),
            headers={
                "Authorization": "Bearer " + Config.pushbullet_token,
                "Content-Type": "application/json",
            },
        )
        if resp.status_code != 200:
            raise Exception("Error", resp.status_code)
        else:
            print("Message sent")

    def handle_the_unexpected_exception(self, err) -> None:
        print(err)
        title = "CMARKETCAP - Unexpected error happened"
        body = f"{err}\n{traceback.format_exc()}"
        self.send_pushbullet_message(title=title, body=body)


if __name__ == "__main__":
    watcher = CMarketCapWatcher()
    watcher.check_the_situation()
