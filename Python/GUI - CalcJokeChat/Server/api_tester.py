import requests
import time
from config import Config

import chat_logic_new

endpoint = Config.endpoint
chat_messages_endpoint = Config.chat_messages_endpoint
latest_updates_endpoint = Config.latest_updates_endpoint


def send_message_old():
    name = "Support"
    message = "How can I help you?"
    key_to_save = "new_features"
    timestamp = int(time.time())
    data = {
        "key_to_save": key_to_save,
        "data": {"name": name, "message": message, "timestamp": timestamp},
    }
    response = requests.post(endpoint, json=data)
    print(response)


def get_messages_old(chat_name="exe_chat"):
    response = requests.get(endpoint)
    content = response.json()

    chat_messages = content.get(chat_name, [])
    print(chat_messages)
    return chat_messages


def announce_new_version_old():
    key_to_save = "last_update"
    timestamp = int(time.time())
    data = {"key_to_save": key_to_save, "data": {"timestamp": timestamp}}
    response = requests.post(endpoint, json=data)
    print(response)


def get_last_updates_old():
    response = requests.get(endpoint)
    content = response.json()

    chat_key = "last_update"

    last_updates = content.get(chat_key, [])
    print(last_updates)
    return last_updates


def send_message(chat_name=None, data=None):
    if not data:
        user_name = "Support"
        message = "Hello, are you there? česky neumim?"
        timestamp = time.time()
        details = ""

        data = {
            "user_name": user_name,
            "message": message,
            "timestamp": timestamp,
            "details": details,
        }

    if not chat_name:
        chat_name = "exe_chat"

    data_to_send = {"chat_name": chat_name, "data": data}
    response = requests.post(chat_messages_endpoint, json=data_to_send)
    print(response)


def save_new_latest_version():
    version_identifier = "0.3"
    timestamp = time.time()
    details = ""

    data = {
        "version_identifier": version_identifier,
        "timestamp": timestamp,
        "details": details,
    }

    data_to_send = {"data": data}
    response = requests.post(latest_updates_endpoint, json=data_to_send)
    print(response)


def migrate_old_chats():
    chat_name = "exe_chat"
    old_messages = get_messages_old(chat_name=chat_name)
    for message in old_messages:
        data = {
            "user_name": message.get("name", ""),
            "message": message.get("message", ""),
            "timestamp": message.get("timestamp", 1),
            "details": message.get("details", ""),
        }
        if data.get("user_name") == "User":
            ip_address_of_sender = Config.user_ip
        else:
            ip_address_of_sender = Config.non_user_ip
        chat_logic_new.save_new_message(chat_name, data, ip_address_of_sender)
        # send_message(chat_name=chat_name, data=data)


def get_messages():
    chat_name = "exe_chat"
    last_message_timestamp = 0
    last_message_timestamp = 1604688619.0
    parameters = {"chat_name": chat_name}
    parameters = {
        "chat_name": chat_name,
        "last_message_timestamp": last_message_timestamp,
    }
    response = requests.get(chat_messages_endpoint, params=parameters)
    results = response.json()
    print(results)
    print(len(results))


def get_last_update():
    response = requests.get(latest_updates_endpoint)
    print(response.json())


# send_message_old()
# get_messages_old()
# announce_new_version_old()
# get_last_updates_old()

send_message()
# save_new_latest_version()
# migrate_old_chats()
# get_messages()
# get_last_update()
