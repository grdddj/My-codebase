import os
from typing import Any, Dict
import requests
import time
import re
import threading
import urllib.request
from PIL import Image
from queue import Queue

import json

from config import Config
import chat_logger


class ActionInDifferentThread(threading.Thread):
    def __init__(
        self, queue: Queue, ws=None, user_name: str = "", ip_address: str = ""
    ) -> None:
        threading.Thread.__init__(self)
        self.queue = queue
        self.ws = ws
        self.user_name = user_name
        self.ip_address = ip_address

        self.final_message_to_the_queue: Dict[str, Any] = {"success": True}

        self.log_identifier = "THREADING"

    def run(self) -> None:
        try:
            self.action_to_be_done()
            self.queue.put(self.final_message_to_the_queue)
            self.log_info(
                f"Different thread has finished successfully - {type(self).__name__}"
            )
        except Exception as err:
            self.log_exception(f"Different thread has problems - {err}")
            results = {"success": False, "reason": err}
            self.queue.put(results)

    def action_to_be_done(self) -> None:
        print("WILL BE IMPLEMENTED BY THE SUBCLASSES")

    def send_message_through_websocket_to_all_clients(self, message_data: dict) -> None:
        message_data["ip_address"] = self.ip_address
        json_message_data = json.dumps(message_data)

        self.log_info(f"Sending message through websocket - {json_message_data}")
        self.ws.send(json_message_data)

    def send_chat_data(
        self, message_type: str, message: str, answer_to_message: str = ""
    ) -> None:
        message_data = {
            "message_type": message_type,
            "user_name": self.user_name,
            "message": message,
            "answer_to_message": answer_to_message,
            "timestamp": time.time(),
            "details": "",
        }

        self.send_message_through_websocket_to_all_clients(message_data)

        data_to_send = {"chat_name": Config.CHAT_NAME, "data": message_data}

        self.log_info(f"Sending message to DB - {data_to_send}")
        requests.post(Config.API_URL_CHAT, json=data_to_send)

    def log_info(self, message: str) -> None:
        chat_logger.info(f"{self.log_identifier} - {message}")

    def log_exception(self, message: str) -> None:
        chat_logger.exception(f"{self.log_identifier} - {message}")


class FileUpload(ActionInDifferentThread):
    def __init__(self, queue: Queue, ws, file_path, user_name, ip_address) -> None:
        ActionInDifferentThread.__init__(self, queue, ws, user_name, ip_address)
        self.file_path = file_path
        self.file_name_saved = ""
        self.log_info(f"{type(self).__name__} started - {self.file_path}")

    def action_to_be_done(self) -> None:
        self.upload_the_file_and_get_its_name()
        self.send_file(self.file_name_saved)
        self.final_message_to_the_queue["file_name_saved"] = self.file_name_saved

    def upload_the_file_and_get_its_name(self) -> None:
        with open(self.file_path, "rb") as file:
            response = requests.post(Config.API_URL_FILE_STORAGE, files={"file": file})
        self.file_name_saved = response.json().get("file_name")
        self.log_info(f"File uploaded and name got - {self.file_name_saved}")

    def send_file(self, file_name) -> None:
        self.send_chat_data(message_type="file", message=file_name)


class FileDownload(ActionInDifferentThread):
    def __init__(self, queue: Queue, file_name) -> None:
        ActionInDifferentThread.__init__(self, queue)
        self.file_name = file_name
        self.log_info(f"{type(self).__name__} started - {self.file_name}")

    def action_to_be_done(self) -> None:
        if not os.path.isdir(Config.download_folder):
            os.mkdir(Config.download_folder)

        parameters = {"file_name": self.file_name}

        response = requests.get(Config.API_URL_FILE_STORAGE, params=parameters)

        self.file_name = self.remove_timestamp_and_underscore_from_beginning(
            self.file_name
        )
        file_path_to_save = os.path.join(Config.download_folder, self.file_name)
        with open(file_path_to_save, "wb") as download_file:
            download_file.write(response.content)

        self.final_message_to_the_queue["file_path_to_save"] = file_path_to_save

    @staticmethod
    def remove_timestamp_and_underscore_from_beginning(file_name: str) -> str:
        pattern = r"^\d{10}_"
        pattern_is_matching = re.match(pattern, file_name)
        if pattern_is_matching:
            characters_to_delete = len(pattern_is_matching.group())
            return file_name[characters_to_delete:]
        else:
            return file_name


class LatestUpdateDownload(ActionInDifferentThread):
    def __init__(self, queue: Queue) -> None:
        ActionInDifferentThread.__init__(self, queue)
        self.log_info(f"{type(self).__name__} started")

    def action_to_be_done(self) -> None:
        timestamp = int(time.time())
        path_where_to_save_it = f"Casio_fx-85_CE_X_latest_{timestamp}.exe"
        urllib.request.urlretrieve(Config.latest_version_url, path_where_to_save_it)

        self.final_message_to_the_queue["path_where_to_save_it"] = path_where_to_save_it


class SmileSending(ActionInDifferentThread):
    def __init__(
        self, queue: Queue, ws, user_name: str, smile_type: str, ip_address: str
    ) -> None:
        ActionInDifferentThread.__init__(self, queue, ws, user_name, ip_address)
        self.smile_type = smile_type
        self.log_info(f"{type(self).__name__} started - {self.smile_type}")

    def action_to_be_done(self) -> None:
        self.send_chat_data(message_type="smile", message=self.smile_type)


class MessageSending(ActionInDifferentThread):
    def __init__(
        self,
        queue: Queue,
        ws,
        user_name: str,
        message: str,
        ip_address: str,
        answer_to_message: str,
    ) -> None:
        ActionInDifferentThread.__init__(self, queue, ws, user_name, ip_address)
        self.message = message
        self.answer_to_message = answer_to_message
        self.log_info(f"{type(self).__name__} started - {self.message}")

    def action_to_be_done(self) -> None:
        self.send_chat_data(
            message_type="text",
            message=self.message,
            answer_to_message=self.answer_to_message,
        )


class PictureUpload(ActionInDifferentThread):
    def __init__(
        self, queue: Queue, ws, picture_path: str, user_name: str, ip_address: str
    ) -> None:
        ActionInDifferentThread.__init__(self, queue, ws, user_name, ip_address)
        self.picture_path = picture_path
        self.log_info(f"{type(self).__name__} started - {self.picture_path}")

    def action_to_be_done(self) -> None:
        if not os.path.isdir(Config.picture_folder):
            os.mkdir(Config.picture_folder)

        picture_name = os.path.basename(self.picture_path)
        picture_save_path = os.path.join(Config.picture_folder, picture_name)

        self.transform_picture_to_max_pixels_size_and_save_it(
            self.picture_path, picture_save_path
        )

        self.upload_the_file_and_get_its_name(picture_save_path)

        self.send_picture(self.file_name_saved)

        if self.file_name_saved != picture_name:
            new_picture_save_path = os.path.join(
                Config.picture_folder, self.file_name_saved
            )
            try:
                os.rename(picture_save_path, new_picture_save_path)
                self.log_info(
                    f"Renaming the file from '{picture_save_path}' to '{new_picture_save_path}'"
                )
            except FileExistsError:
                self.log_info(f"File already in place - '{new_picture_save_path}'")

        self.final_message_to_the_queue["file_name_saved"] = self.file_name_saved

    def upload_the_file_and_get_its_name(self, file_path_to_upload: str) -> None:
        with open(file_path_to_upload, "rb") as file:
            response = requests.post(
                Config.API_URL_PICTURE_STORAGE, files={"file": file}
            )
        self.file_name_saved = response.json().get("file_name")
        self.log_info(f"Picture uploaded and name got - {self.file_name_saved}")

    def send_picture(self, picture_name: str) -> None:
        self.send_chat_data(message_type="picture", message=picture_name)

    def transform_picture_to_max_pixels_size_and_save_it(
        self, picture_path: str, picture_save_path: str
    ) -> None:
        max_pixels_size = Config.pictures_max_pixels_size
        orig_image = Image.open(picture_path)
        x_size, y_size = orig_image.size
        max_size = max(x_size, y_size)

        picture_needs_to_be_reduced = max_size > max_pixels_size
        if picture_needs_to_be_reduced:
            if x_size >= y_size:
                ratio = max_pixels_size / x_size
                new_x = max_pixels_size
                new_y = int(y_size * ratio)
            else:
                ratio = max_pixels_size / y_size
                new_y = max_pixels_size
                new_x = int(x_size * ratio)
            im2 = orig_image.resize((new_x, new_y), Image.BICUBIC)
            im2.save(picture_save_path)
            self.log_info(
                f"Picture transformed from {x_size}x{y_size} to {new_x}x{new_y}"
            )
        else:
            orig_image.save(picture_save_path)
            self.log_info(f"Picture did not need any transforming - {picture_path}")
