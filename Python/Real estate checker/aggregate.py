import logger
from all_flats import fetch_and_update_all_new_flats
from flat_details import add_details_to_all_flats


def aggregate_the_fetch():
    logger.log_info("Starting the script")

    fetch_and_update_all_new_flats()
    add_details_to_all_flats()

    logger.log_info("Finishing the script")


if __name__ == "__main__":
    try:
        aggregate_the_fetch()
    except Exception as err:
        logger.log_exception(err)
        raise
