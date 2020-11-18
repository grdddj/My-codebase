import websocket
import time
import json

from config import Config

ws = websocket.create_connection(Config.MESSAGES_WEBSOCKET_URL)

message_obj = [{
    "user_name": "my_name",
    "message_type": "text",
    "message": "my_message",
    "timestamp": time.time(),
    "ip_address": "123456",
    "details": "",
}]

json_msg = json.dumps(message_obj)
ws.send(json_msg)

ws.close()
