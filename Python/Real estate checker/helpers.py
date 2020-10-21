import os
import time
from datetime import datetime


def make_dir_if_not_exists(dir_path):
    if not os.path.isdir(dir_path):
        os.mkdir(dir_path)


# TODO: find the way how to make it work (increment the global counter)
def print_and_increment_counter(counter, total_count):
    counter += 1
    print(counter, "/", total_count)


def get_current_ts():
    return int(time.time())


def get_current_date():
    current_ts = get_current_ts()
    return datetime.fromtimestamp(current_ts).strftime('%Y-%m-%d')
