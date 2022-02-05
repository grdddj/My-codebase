from flask import Flask, jsonify, request, send_from_directory
from flask_restful import reqparse, Resource, Api
from flask_cors import CORS
import werkzeug
from werkzeug.utils import secure_filename

import time

# Necessary for deployment on the server
import os
import sys

MODULE_DIR_PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, MODULE_DIR_PATH)

import chat_logic_old
import chat_logic_new


app = Flask(__name__)
api = Api(app)

CORS(app)


class DB_content_old(Resource):
    post_parser = reqparse.RequestParser()
    post_parser.add_argument("key_to_save", type=str, location="json")
    post_parser.add_argument("data", type=dict, location="json")

    def get(self):
        results = chat_logic_old.get_results()

        return jsonify(results)

    def post(self):
        request_data = self.post_parser.parse_args()

        chat_logic_old.process_post(request_data)

        # passing the old content to the new db
        chat_name = request_data["key_to_save"]
        ip_address_of_sender = request.remote_addr
        data = {
            "user_name": request_data["data"].get("name", ""),
            "timestamp": request_data["data"].get("timestamp", 1),
            "message": request_data["data"].get("message", ""),
            "answer_to_message": request_data["data"].get("answer_to_message", ""),
            "message_type": request_data["data"].get("message_type", "text"),
            "details": "",
        }
        chat_logic_new.save_new_message(
            chat_name=chat_name, data=data, ip_address_of_sender=ip_address_of_sender
        )

        return "Processed"


class IPAddress(Resource):
    def get(self):
        ip_address_of_sender = request.remote_addr
        results = {"ip_address": ip_address_of_sender}

        return jsonify(results)


class Chat(Resource):
    get_parser = reqparse.RequestParser()
    get_parser.add_argument("chat_name", type=str)
    get_parser.add_argument("last_message_timestamp", type=float)
    get_parser.add_argument("max_result_size", type=int)

    post_parser = reqparse.RequestParser()
    post_parser.add_argument("chat_name", type=str, location="json")
    post_parser.add_argument("data", type=dict, location="json")

    def get(self):
        request_data = self.get_parser.parse_args()

        chat_name = request_data["chat_name"]
        last_message_timestamp = request_data["last_message_timestamp"]
        max_result_size = request_data["max_result_size"]
        # Defending against the arguments not even sent with the request
        if last_message_timestamp is None:
            last_message_timestamp = 0
        if max_result_size is None:
            max_result_size = 9999999999

        results = chat_logic_new.get_chat_messages(
            chat_name=chat_name,
            last_message_timestamp=last_message_timestamp,
            max_result_size=max_result_size,
        )

        # TODO: could also store a timestamp that this IP was online at that time

        return jsonify(results)

    def post(self):
        request_data = self.post_parser.parse_args()

        chat_name = request_data["chat_name"]
        data = request_data["data"]

        ip_address_of_sender = request.remote_addr

        chat_logic_new.save_new_message(
            chat_name=chat_name, data=data, ip_address_of_sender=ip_address_of_sender
        )

        return "Message saved"


class LastUpdate(Resource):
    post_parser = reqparse.RequestParser()
    post_parser.add_argument("data", type=dict, location="json")

    def get(self):
        results = chat_logic_new.get_last_update()

        return jsonify(results)

    def post(self):
        request_data = self.post_parser.parse_args()

        data = request_data["data"]

        chat_logic_new.save_last_update(data)

        return "Last update saved"


class FileStorage(Resource):
    get_parser = reqparse.RequestParser()
    get_parser.add_argument("file_name", type=str)

    post_parser = reqparse.RequestParser()
    post_parser.add_argument(
        "file", type=werkzeug.datastructures.FileStorage, location="files"
    )

    def get(self):
        request_data = self.get_parser.parse_args()

        file_name = request_data["file_name"]

        folder_location = os.path.join(MODULE_DIR_PATH, "files")

        return send_from_directory(folder_location, file_name)

    def post(self):
        request_data = self.post_parser.parse_args()

        file = request_data["file"]
        file_name = get_secure_unique_filename(file)

        folder_location = os.path.join(MODULE_DIR_PATH, "files")
        file_path = os.path.join(folder_location, file_name)
        file.save(file_path)

        results = {"file_name": file_name}
        return jsonify(results)


class PictureStorage(Resource):
    get_parser = reqparse.RequestParser()
    get_parser.add_argument("file_name", type=str)

    post_parser = reqparse.RequestParser()
    post_parser.add_argument(
        "file", type=werkzeug.datastructures.FileStorage, location="files"
    )

    def get(self):
        request_data = self.get_parser.parse_args()

        file_name = request_data["file_name"]

        folder_location = os.path.join(MODULE_DIR_PATH, "pictures")

        return send_from_directory(folder_location, file_name)

    def post(self):
        request_data = self.post_parser.parse_args()

        file = request_data["file"]
        file_name = get_secure_unique_filename(file)

        folder_location = os.path.join(MODULE_DIR_PATH, "pictures")
        file_path = os.path.join(folder_location, file_name)
        file.save(file_path)

        results = {"file_name": file_name}
        return jsonify(results)


def get_secure_unique_filename(file):
    timestamp = str(int(time.time()))
    return timestamp + "_" + secure_filename(file.filename)


api.add_resource(DB_content_old, "/db_content")
api.add_resource(IPAddress, "/v1/ip_address")
api.add_resource(Chat, "/v1/chat")
api.add_resource(LastUpdate, "/v1/last_update")
api.add_resource(FileStorage, "/v1/file_storage")
api.add_resource(PictureStorage, "/v1/picture_storage")


if __name__ == "__main__":
    app.run(port="5678", debug=True)
