import websocket

from config import Config

ws = websocket.create_connection(Config.MESSAGES_WEBSOCKET_URL)
while True:
    new_messages = ws.recv()
    print(new_messages)
