# Necessary for deployment on the server
import os
import sys
MODULE_DIR_PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, MODULE_DIR_PATH)

from chat_db import return_engine_and_session, ChatMessage, LastUpdate

_, session = return_engine_and_session()


def save_new_message(chat_name, data, ip_address_of_sender):
    user_name = data.get("user_name", "")
    message = data.get("message", "")
    timestamp = data.get("timestamp", 0)
    details = data.get("details", "")

    new_message = ChatMessage(
        chat_name=chat_name,
        user_name=user_name,
        message=message,
        timestamp=timestamp,
        ip_address=ip_address_of_sender,
        details=details
    )

    session.add(new_message)
    session.commit()


def get_chat_messages(chat_name, last_message_timestamp):
    chat_messages = session.query(ChatMessage) \
        .filter(ChatMessage.chat_name == chat_name) \
        .filter(ChatMessage.timestamp > last_message_timestamp) \
        .order_by(ChatMessage.id) \
        .all()

    list_to_return = []
    for message in chat_messages:
        message_object = {
            "user_name": message.user_name,
            "message": message.message,
            "timestamp": message.timestamp,
            "ip_address": message.ip_address,
            "details": message.details,
        }
        list_to_return.append(message_object)

    return list_to_return


def save_last_update(data):
    version_identifier = data.get("version_identifier", "")
    timestamp = data.get("timestamp", 0)
    details = data.get("details", "")

    last_update = LastUpdate(
        version_identifier=version_identifier,
        timestamp=timestamp,
        details=details
    )

    session.add(last_update)
    session.commit()


def get_last_update():
    last_update = session.query(LastUpdate) \
        .order_by(LastUpdate.id.desc()) \
        .first()

    last_update_object = {
        "version_identifier": last_update.version_identifier,
        "timestamp": last_update.timestamp,
        "details": last_update.details,
    }

    return last_update_object
