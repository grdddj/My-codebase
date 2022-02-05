import os
import time
from datetime import datetime


def make_dir_if_not_exists(dir_path: str) -> None:
    if not os.path.isdir(dir_path):
        os.mkdir(dir_path)


# TODO: find the way how to make it work (increment the global counter)
def print_and_increment_counter(counter, total_count):
    counter += 1
    print(counter, "/", total_count)


def get_current_ts() -> int:
    return int(time.time())


def get_current_date() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def get_timestamp_from_formatted_date(formatted_date: str) -> int:
    return int(datetime.strptime(formatted_date, "%Y-%m-%d").timestamp())
