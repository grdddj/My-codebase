import logging

log_file_path = "chat_logs.txt"

logging.basicConfig(
    filename=log_file_path,
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)


def info(message):
    logging.info(message)


def warning(message):
    logging.warning(message)


def error(message):
    logging.error(message)


def exception(message):
    logging.exception(message)
