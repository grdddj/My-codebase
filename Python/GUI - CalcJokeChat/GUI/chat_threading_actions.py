import os
import requests
import time
import re
import threading
import urllib.request
from PIL import Image

from config import Config


class GettingMessageData(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue

        self._stop_event = threading.Event()

        self.last_message_timestamp = 0

    def stop(self):
        print("stopping the background thread")
        self._stop_event.set()
        threading.Thread.join(self, None)

    def is_stopped(self):
        return self._stop_event.is_set()

    def run(self):
        while True:
            if self.is_stopped():
                break

            try:
                new_messages = self.get_new_chat_messages()
                if new_messages:
                    self.last_message_timestamp = new_messages[-1]["timestamp"]
                    self.queue.put(new_messages)
            except Exception as err:
                print("exception when getting messages", err)
            finally:
                time.sleep(Config.time_to_sleep_between_getting_messages)

    def get_new_chat_messages(self):
        # TODO: somehow handle the case of timeout (gracefully, so user does not even notice)
        parameters = {
            "chat_name": Config.CHAT_NAME,
            "last_message_timestamp": self.last_message_timestamp,
            "max_result_size": Config.how_many_messages_to_load_at_startup
        }
        response = requests.get(Config.API_URL_CHAT, params=parameters, timeout=1)
        new_chat_messages = response.json()

        return new_chat_messages


class ActionInDifferentThread(threading.Thread):
    def __init__(self, queue, user_name=""):
        threading.Thread.__init__(self)
        self.queue = queue
        self.user_name = user_name

        self.final_message_to_the_queue = {"success": True}

    def run(self):
        try:
            self.action_to_be_done()
            self.queue.put(self.final_message_to_the_queue)
        except Exception as err:
            results = {"success": False, "reason": err}
            self.queue.put(results)

    def action_to_be_done(self):
        print("WILL BE IMPLEMENTED BY THE SUBCLASSES")

    def send_chat_data(self, message_type, message):
        data = {
            "message_type": message_type,
            "user_name": self.user_name,
            "message": message,
            "timestamp": time.time(),
            "details": ""
        }
        data_to_send = {"chat_name": Config.CHAT_NAME, "data": data}

        requests.post(Config.API_URL_CHAT, json=data_to_send)


class FileUpload(ActionInDifferentThread):
    def __init__(self, queue, file_path, user_name):
        ActionInDifferentThread.__init__(self, queue, user_name)
        self.file_path = file_path

        self.file_name_saved = ""

    def action_to_be_done(self):
        self.upload_the_file_and_get_its_name()
        self.send_file(self.file_name_saved)
        self.final_message_to_the_queue["file_name_saved"] = self.file_name_saved

    def upload_the_file_and_get_its_name(self):
        with open(self.file_path, 'rb') as file:
            response = requests.post(Config.API_URL_FILE_STORAGE, files={'file': file})
        self.file_name_saved = response.json().get("file_name")

    def send_file(self, file_name):
        self.send_chat_data(message_type="file", message=file_name)


class FileDownload(ActionInDifferentThread):
    def __init__(self, queue, file_name):
        ActionInDifferentThread.__init__(self, queue)
        self.file_name = file_name

    def action_to_be_done(self):
        if not os.path.isdir(Config.download_folder):
            os.mkdir(Config.download_folder)

        parameters = {"file_name": self.file_name}

        response = requests.get(Config.API_URL_FILE_STORAGE, params=parameters)

        self.file_name = self.remove_timestamp_and_underscore_from_beginning(self.file_name)
        file_path_to_save = os.path.join(Config.download_folder, self.file_name)
        with open(file_path_to_save, 'wb') as download_file:
            download_file.write(response.content)

        self.final_message_to_the_queue["file_path_to_save"] = file_path_to_save

    @staticmethod
    def remove_timestamp_and_underscore_from_beginning(file_name):
        pattern = r"^\d{10}_"
        pattern_is_matching = re.match(pattern, file_name)
        if pattern_is_matching:
            characters_to_delete = len(pattern_is_matching.group())
            return file_name[characters_to_delete:]
        else:
            return file_name


class LatestUpdateDownload(ActionInDifferentThread):
    def __init__(self, queue):
        ActionInDifferentThread.__init__(self, queue)

    def action_to_be_done(self):
        timestamp = int(time.time())
        path_where_to_save_it = f"Casio_fx-85_CE_X_latest_{timestamp}.exe"
        urllib.request.urlretrieve(Config.latest_version_url, path_where_to_save_it)

        self.final_message_to_the_queue["path_where_to_save_it"] = path_where_to_save_it


class SmileSending(ActionInDifferentThread):
    def __init__(self, queue, user_name, smile_type):
        ActionInDifferentThread.__init__(self, queue, user_name)
        self.smile_type = smile_type

    def action_to_be_done(self):
        self.send_chat_data(message_type="smile", message=self.smile_type)


class MessageSending(ActionInDifferentThread):
    def __init__(self, queue, user_name, message):
        ActionInDifferentThread.__init__(self, queue, user_name)
        self.message = message

    def action_to_be_done(self):
        self.send_chat_data(message_type="text", message=self.message)


class PictureUpload(ActionInDifferentThread):
    def __init__(self, queue, picture_path, user_name):
        ActionInDifferentThread.__init__(self, queue, user_name)
        self.picture_path = picture_path

    def action_to_be_done(self):
        if not os.path.isdir(Config.picture_folder):
            os.mkdir(Config.picture_folder)

        picture_name = os.path.basename(self.picture_path)
        picture_save_path = os.path.join(Config.picture_folder, picture_name)

        self.transform_picture_to_max_pixels_size_and_save_it(
            self.picture_path, picture_save_path)

        self.upload_the_file_and_get_its_name(picture_save_path)

        self.send_picture(self.file_name_saved)

        if self.file_name_saved != picture_name:
            new_picture_save_path = os.path.join(Config.picture_folder, self.file_name_saved)
            os.rename(picture_save_path, new_picture_save_path)

        self.final_message_to_the_queue["file_name_saved"] = self.file_name_saved

    def upload_the_file_and_get_its_name(self, file_path_to_upload):
        with open(file_path_to_upload, 'rb') as file:
            response = requests.post(Config.API_URL_PICTURE_STORAGE, files={'file': file})
        self.file_name_saved = response.json().get("file_name")

    def send_picture(self, picture_name):
        self.send_chat_data(message_type="picture", message=picture_name)

    @staticmethod
    def transform_picture_to_max_pixels_size_and_save_it(picture_path, picture_save_path):
        max_pixels_size = Config.pictures_max_pixels_size
        orig_image = Image.open(picture_path)
        x_size, y_size = orig_image.size
        max_size = max(x_size, y_size)

        picture_needs_to_be_reduced = max_size > max_pixels_size
        if picture_needs_to_be_reduced:
            if x_size >= y_size:
                ratio = (max_pixels_size / x_size)
                new_x = max_pixels_size
                new_y = int(y_size * ratio)
            else:
                ratio = (max_pixels_size / y_size)
                new_y = max_pixels_size
                new_x = int(x_size * ratio)
            im2 = orig_image.resize((new_x, new_y), Image.BICUBIC)
            im2.save(picture_save_path)
        else:
            orig_image.save(picture_save_path)
