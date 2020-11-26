import requests
from datetime import datetime

from config import Config


def get_ip_address():
    response = requests.get(Config.API_URL_IP)
    ip_address_json = response.json()
    return ip_address_json["ip_address"]


def is_date_from_today(dt_object):
    today_dt_object = datetime.now()
    today_morning = datetime(year=today_dt_object.year, month=today_dt_object.month,
                             day=today_dt_object.day, hour=0, second=0)
    message_is_from_today = today_morning < dt_object
    return message_is_from_today


def define_entry_content(entry_component, content_to_fill):
    entry_component["state"] = "normal"
    entry_component.delete(0, "end")
    entry_component.insert(0, content_to_fill)
    entry_component["state"] = "disabled"
