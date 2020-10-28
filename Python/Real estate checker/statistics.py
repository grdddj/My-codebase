import json
import os
import re
from datetime import datetime

WORKING_DIRECTORY = os.path.dirname(os.path.realpath(__file__))

results_file = "results.json"
results_file = os.path.join(WORKING_DIRECTORY, results_file)

# TODO: have some nice table generated into the command line


def get_results():
    with open(results_file, 'r', encoding='utf-8') as my_file:
        results = json.load(my_file)
        results_list = list(results.values())
        return results_list


def overall_number_of_flats_we_have():
    results = get_results()
    number_of_results = len(results)

    print("number_of_results", number_of_results)
    return number_of_results


def changed_prices():
    key = "price"
    return changed_value_of(key)


def changed_offer_state():
    key = "state_of_offer"
    return changed_value_of(key)


def changed_value_of(key):
    key_history = "{}_history".format(key)
    results = get_results()
    changed_flats = []
    for result in results:
        if key_history in result:
            changed_flats.append(result)

    return changed_flats


def average_price():
    results = get_results()
    return get_average_price(results)


def get_average_price(results):
    number_of_results = len(results)
    combined_price = sum([flat["price"] for flat in results])
    average_price = combined_price // number_of_results

    print("average_price", average_price)
    return average_price


def median_price():
    results = get_results()
    return get_median_price(results)


def get_median_price(results):
    prices = [flat["price"] for flat in results]
    number_of_prices = len(prices)
    price_sorted_results = sorted(prices)
    half_in_results = number_of_prices // 2
    median_price = price_sorted_results[half_in_results]

    print("median_price", median_price)
    return median_price


def amount_of_types():
    # TODO: implement this
    return {"2+kk": 51}


def new_today():
    today_date = datetime.now().strftime('%Y-%m-%d')
    results = get_results()

    key = "first_seen_date"
    value = today_date

    matching_results = get_results_with_exact_key_value(results, key, value)

    print("matching_results", len(matching_results))

    return matching_results


def not_active_anymore():
    today_date = datetime.now().strftime('%Y-%m-%d')
    results = get_results()

    key = "last_update_date"
    value = today_date

    matching_results = get_results_with_different_key_value(results, key, value)

    print("matching_results", len(matching_results))

    return matching_results


def get_results_with_exact_key_value(results, key, value):
    matching_results = [result for result in results if result.get(key) == value]
    return matching_results


def get_results_with_different_key_value(results, key, value):
    matching_results = [result for result in results if result.get(key) != value]
    return matching_results


def flat_containing_some_text(text):
    text_pattern = re.compile(r'{}'.format(text), re.IGNORECASE)
    matching_results = []
    results = get_results()
    for result in results:
        if text_pattern.search(str(result)):
            matching_results.append(result)

    print("matching_results", len(matching_results))
    return matching_results


if __name__ == "__main__":
    # overall_number_of_flats_we_have()
    # changed_prices()
    # changed_offer_state()
    # amount_of_types()
    # average_price()
    # median_price()
    # new_today()
    # not_active_anymore()
    flat_containing_some_text("útulný")
