import logging

log_file_path = "chat_logs.txt"

logging.basicConfig(
    filename=log_file_path,
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)


def info(message: str) -> None:
    logging.info(message)


def warning(message: str) -> None:
    logging.warning(message)


def error(message: str) -> None:
    logging.error(message)


def exception(message: str) -> None:
    logging.exception(message)
