from flask import Flask, jsonify, request
from flask_restful import reqparse, Resource, Api
from flask_cors import CORS

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
    post_parser.add_argument('key_to_save', type=str, location='json')
    post_parser.add_argument('data', type=dict, location='json')

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
            "details": ""
        }
        chat_logic_new.save_new_message(chat_name=chat_name,
                                        data=data,
                                        ip_address_of_sender=ip_address_of_sender)

        return "Processed"


class Chat(Resource):
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('chat_name', type=str)
    get_parser.add_argument('last_message_timestamp', type=float)

    post_parser = reqparse.RequestParser()
    post_parser.add_argument('chat_name', type=str, location='json')
    post_parser.add_argument('data', type=dict, location='json')

    def get(self):
        request_data = self.get_parser.parse_args()

        chat_name = request_data["chat_name"]
        last_message_timestamp = request_data["last_message_timestamp"]
        # Defending against the argument not even sent with the request
        if last_message_timestamp is None:
            last_message_timestamp = 0

        results = chat_logic_new.get_chat_messages(
            chat_name=chat_name,
            last_message_timestamp=last_message_timestamp)

        # TODO: could also store a timestamp that this IP was online at that time

        return jsonify(results)

    def post(self):
        request_data = self.post_parser.parse_args()

        chat_name = request_data["chat_name"]
        data = request_data["data"]

        ip_address_of_sender = request.remote_addr

        chat_logic_new.save_new_message(chat_name=chat_name,
                                        data=data,
                                        ip_address_of_sender=ip_address_of_sender)

        return "Message saved"


class LastUpdate(Resource):
    post_parser = reqparse.RequestParser()
    post_parser.add_argument('data', type=dict, location='json')

    def get(self):
        results = chat_logic_new.get_last_update()

        return jsonify(results)

    def post(self):
        request_data = self.post_parser.parse_args()

        data = request_data["data"]

        chat_logic_new.save_last_update(data)

        return "Last update saved"


api.add_resource(DB_content_old, '/db_content')
api.add_resource(Chat, '/v1/chat')
api.add_resource(LastUpdate, '/v1/last_update')


if __name__ == '__main__':
    app.run(port='5678', debug=True)
