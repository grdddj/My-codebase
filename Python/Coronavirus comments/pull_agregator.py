"""
The aggregator of all scripts to carry out the whole pull of the articles
    and comments
"""

import os
import sys
import time
import logging

from get_corona_articles import save_links_into_file
from discussion_selenium import fetch_comments_for_all_articles_from_file_into_a_folder
from reader_into_db import save_all_files_from_a_folder_into_db

WORKING_DIRECTORY = os.path.dirname(os.path.realpath(__file__))

# Using logging as a neat way to find out errors in production
error_filename = "error_logs.log"
error_filename_full = os.path.join(WORKING_DIRECTORY, error_filename)
logging.basicConfig(filename=error_filename_full,
                    level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')

# Trying to get a number of clicks from a command line, otherwise going with default
try:
    amount_of_next_clicks = int(sys.argv[1])
except (IndexError, ValueError):
    logging.warning("badly inputted number of clicks")
    amount_of_next_clicks = 5

begin_timestamp = int(time.time())
file_path = "{}.json".format(begin_timestamp)
folder_name = str(begin_timestamp)

# We need full paths because we want to call it from cron
full_file_path = os.path.join(WORKING_DIRECTORY, file_path)
full_folder_name = os.path.join(WORKING_DIRECTORY, folder_name)

# Logging the start with parameters
logging.info("{} - We are starting - clicks: {}".format(
    begin_timestamp, amount_of_next_clicks))

# Calling those procedures and logging potential errors
try:
    save_links_into_file(full_file_path, amount_of_next_clicks)
    logging.info("{} - finished script - save links".format(begin_timestamp))
    fetch_comments_for_all_articles_from_file_into_a_folder(full_file_path, full_folder_name)
    logging.info("{} - finished script - fetch comments".format(begin_timestamp))
    save_all_files_from_a_folder_into_db(full_folder_name)
    logging.info("{} - finished script - save into DB".format(begin_timestamp))
except Exception as e:
    logging.exception(e)
else:
    logging.info("{} - We are finished. Took {} s to get {} pages".format(
        begin_timestamp, int(time.time()) - begin_timestamp, amount_of_next_clicks + 1))
