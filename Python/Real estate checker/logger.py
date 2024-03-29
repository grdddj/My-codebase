import logging
import os

WORKING_DIRECTORY = os.path.dirname(os.path.realpath(__file__))

log_filename = "sreality.log"
log_filename = os.path.join(WORKING_DIRECTORY, log_filename)

logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)


def log_exception(e) -> None:
    logging.exception(e)


def log_error(error) -> None:
    logging.error(error)


def log_info(info) -> None:
    logging.info(info)
