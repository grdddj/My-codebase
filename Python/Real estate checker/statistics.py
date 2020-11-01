import json
import os
import sys
import re
from datetime import datetime
from collections import defaultdict

import helpers

WORKING_DIRECTORY = os.path.dirname(os.path.realpath(__file__))

results_file = "results.json"
results_file = os.path.join(WORKING_DIRECTORY, results_file)

# TODO: have some nice table generated into the command line


def _get_results():
    with open(results_file, 'r', encoding='utf-8') as my_file:
        results = json.load(my_file)
        results_list = list(results.values())
        return results_list


def overall_number_of_flats_we_have():
    results = _get_results()
    number_of_results = len(results)

    print("Total amount of flats:", number_of_results)
    return number_of_results


def _changed_prices():
    key = "price"
    return _changed_value_of(key)


def display_details_of_changed_prices():
    changed_prices_flats = _changed_prices()
    changed_prices_flats_sorted = _get_sorted_by_last_change("price_history", changed_prices_flats)
    for flat in changed_prices_flats_sorted:
        _print_basic_info(flat)
        price_history = flat["price_history"]
        for entry in price_history:
            _print_change_in_time("price", entry)
        _print_horizontal_divide()


def _get_sorted_by_last_change(field_of_change, flats):
    return sorted(flats, key=lambda flat: helpers.get_timestamp_from_formatted_date(
                  flat[field_of_change][-1]["date"]))


def some_offer_state():
    results = _get_results()
    key = "state_of_offer"
    flats_changed_offer = _get_results_with_specific_key(results, key)
    for flat in flats_changed_offer:
        _print_basic_info(flat)
        print(flat["state_of_offer"])
        _print_horizontal_divide()


def _changed_value_of(key):
    key_history = "{}_history".format(key)
    results = _get_results()
    changed_flats = [result for result in results if key_history in result]

    return changed_flats


def average_price():
    results = _get_results()
    average_price = _get_average_price(results)
    print("Average price", f"{average_price:,}")

    return average_price


def _get_average_price(results):
    number_of_results = len(results)
    combined_price = sum([flat["price"] for flat in results])
    average_price = combined_price // number_of_results

    return average_price


def median_price():
    results = _get_results()
    median_price = _get_median_price(results)
    print("Median price", f"{median_price:,}")

    return median_price


def _get_median_price(results):
    prices = [flat["price"] for flat in results]
    number_of_prices = len(prices)
    price_sorted_results = sorted(prices)
    half_in_results = number_of_prices // 2
    median_price = price_sorted_results[half_in_results]

    return median_price


def amount_of_types():
    results = _get_results()
    types = defaultdict(int)
    for result in results:
        type = result["type"]
        types[type] += 1

    sorted_types = sorted(types.items(), key=lambda x: x[1], reverse=True)
    for type, amount in sorted_types:
        print(f"{type} - {amount}")
    return sorted_types


def new_today():
    today_date = datetime.now().strftime('%Y-%m-%d')
    results = _get_results()

    key = "first_seen_date"
    value = today_date

    matching_results = _get_results_with_exact_key_value(results, key, value)

    for flat in matching_results:
        _print_basic_info(flat)
        print(flat["description"])
        _print_horizontal_divide()

    print("Flats new today:", len(matching_results))

    return matching_results


def not_active_anymore():
    today_date = datetime.now().strftime('%Y-%m-%d')
    results = _get_results()

    key = "last_update_date"
    value = today_date

    matching_results = _get_results_with_different_key_value(results, key, value)

    print("Flats not active anymore:", len(matching_results))

    return matching_results


def _get_results_with_specific_key(results, key):
    matching_results = [result for result in results if key in result]
    return matching_results


def _get_results_with_exact_key_value(results, key, value):
    matching_results = [result for result in results if result.get(key) == value]
    return matching_results


def _get_results_with_different_key_value(results, key, value):
    matching_results = [result for result in results if result.get(key) != value]
    return matching_results


def show_flat_containing_some_text():
    text = input("Text: ")
    return flat_containing_some_text(text)


def flat_containing_some_text(text):
    text_pattern = re.compile(r'{}'.format(text), re.IGNORECASE)
    results = _get_results()
    matching_results = [result for result in results if text_pattern.search(str(result))]

    for flat in matching_results:
        _print_basic_info(flat)
        print(flat["description"])
        _print_horizontal_divide()

    print("matching_results", len(matching_results))
    return matching_results


def show_specific_flat():
    flat_id = input("Flat ID: ")
    return get_specific_flat(flat_id)


def get_specific_flat(flat_id):
    results = _get_results()
    flats = _get_results_with_exact_key_value(results, "flat_id", flat_id)

    if len(flats) < 1:
        print("Impossible to locate this ID")
    else:
        for key, value in flats[0].items():
            print(key, value)

    return flats


def new_flats_each_day():
    results = _get_results()
    _aggregate_info_by_time(results, "first_seen_date")


def sold_flats_each_day():
    results = _get_results()
    _aggregate_info_by_time(results, "last_update_date")


def _aggregate_info_by_time(results, key):
    days_and_values = defaultdict(int)
    for result in results:
        value = result[key]
        days_and_values[value] += 1

    sorted_by_time = sorted(days_and_values.items(),
        key=lambda x: helpers.get_timestamp_from_formatted_date(x[0]))

    for day, flat_amount in sorted_by_time:
        print(day, flat_amount)


def _print_basic_info(flat):
    type = flat["type"]
    area = flat["area_in_square_meters"]
    locality = flat["locality"]
    last_update = flat["last_update_date"]
    link = flat["link"]
    price = flat["price"]

    print(f"{type}, {area} m2, {locality}")
    print(f"{price:,}")
    if last_update == helpers.get_current_date():
        print(link)
    else:
        print(f"S{80*'O'}LD on {last_update}")


def _print_change_in_time(field_changed, entry):
    date = entry['date']
    value_changed = entry[field_changed]
    if isinstance(value_changed, int):
        value_changed = f"{value_changed:,}"
    change_info = f"{date} - {value_changed}"
    print(change_info)


def _print_horizontal_divide():
    print(80*"*")


if __name__ == "__main__":
    # (description, keyword, function)
    query_to_function = [
        ("Total amount of flats we have", "total", overall_number_of_flats_we_have),
        ("Flats changed prices recently", "changed_price", display_details_of_changed_prices),
        ("Some offer state", "offer_state", some_offer_state),
        ("Amount of specific types", "types", amount_of_types),
        ("Average price", "average_price", average_price),
        ("Median price", "median_price", median_price),
        ("Flats new today", "new_today", new_today),
        ("Flats not active anymore", "not_active_anymore", not_active_anymore),
        ("Flats containing some text", "some_text", show_flat_containing_some_text),
        ("Show specific flat", "specific_id", show_specific_flat),
        ("New flats each day", "daily_new", new_flats_each_day),
        ("Sold each day", "daily_sold", sold_flats_each_day),
    ]

    # TODO: create querying logic like "today" "sold", etc. to filter any query

    if len(sys.argv) > 1:
        query = sys.argv[1]
        # Looking for the right query and triggering that function
        for q_t_f in query_to_function:
            if query == q_t_f[1]:
                q_t_f[-1]()
                exit(0)
        print("No argument like that - ", query)
    else:
        # Showing the possibilities
        for index, q_t_f in enumerate(query_to_function):
            print(f"({index}) - {q_t_f[1]} - {q_t_f[0]}")

        try:
            number = input("Which one? ")
            _print_horizontal_divide()
            query_to_function[int(number)][-1]()
        except (ValueError, IndexError) as e:
            print("That is probably a bad input, try again")
            print(e)
