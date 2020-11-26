import requests
import time
import threading

import json

from config import Config


class ActionInDifferentThread(threading.Thread):
    def __init__(self, queue, ws=None, user_name="", ip_address=""):
        threading.Thread.__init__(self)
        self.queue = queue
        self.ws = ws
        self.user_name = user_name
        self.ip_address = ip_address

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

    def send_message_through_websocket_to_all_clients(self, message_data):
        message_data["ip_address"] = self.ip_address
        json_message_data = json.dumps(message_data)

        self.ws.send(json_message_data)

    def send_chat_data(self, message_type, message, answer_to_message=""):
        message_data = {
            "message_type": message_type,
            "user_name": self.user_name,
            "message": message,
            "answer_to_message": answer_to_message,
            "timestamp": time.time(),
            "details": ""
        }

        self.send_message_through_websocket_to_all_clients(message_data)

        data_to_send = {"chat_name": Config.CHAT_NAME, "data": message_data}

        requests.post(Config.API_URL_CHAT, json=data_to_send)


class MessageSending(ActionInDifferentThread):
    def __init__(self, queue, ws, user_name, message, ip_address, answer_to_message):
        ActionInDifferentThread.__init__(self, queue, ws, user_name, ip_address)
        self.message = message
        self.answer_to_message = answer_to_message

    def action_to_be_done(self):
        self.send_chat_data(message_type="text", message=self.message,
                            answer_to_message=self.answer_to_message)
