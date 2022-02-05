import json

import requests

from config import Config


def send_pushbullet_message(title: str, body: str) -> None:
    msg = {"type": "note", "title": title, "body": body}
    resp = requests.post(
        "https://api.pushbullet.com/v2/pushes",
        data=json.dumps(msg),
        headers={
            "Authorization": "Bearer " + Config.TOKEN,
            "Content-Type": "application/json",
        },
    )
    if resp.status_code != 200:
        raise Exception("Error", resp.status_code)
    else:
        print("Message sent")
