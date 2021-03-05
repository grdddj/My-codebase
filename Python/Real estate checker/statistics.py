import json
import os
import sys
import re
from datetime import datetime, timedelta
from collections import defaultdict
from tabulate import tabulate
# TODO: have some nice table generated into the command line

import helpers


class Statistics:
    def __init__(self):
        WORKING_DIRECTORY = os.path.dirname(os.path.realpath(__file__))

        results_file = "results.json"
        self.results_file = os.path.join(WORKING_DIRECTORY, results_file)

    def _get_results(self):
        with open(self.results_file, 'r', encoding='utf-8') as my_file:
            results = json.load(my_file)
            results_list = list(results.values())
            return results_list

    def overall_number_of_flats_we_have(self):
        results = self._get_results()
        number_of_results = len(results)

        print("Total amount of flats:", number_of_results)
        return number_of_results

    def _changed_prices(self):
        key = "price"
        return self._changed_value_of(key)

    def display_details_of_changed_prices(self):
        changed_prices_flats = self._changed_prices()
        changed_prices_flats_sorted = self._get_sorted_by_last_change(
            "price_history", changed_prices_flats)

        data = []
        for flat in changed_prices_flats_sorted:
            info = self._get_basic_info(flat)

            relevant_price_history = [entry for entry in flat["price_history"] if entry["price"] != 1]
            if len(relevant_price_history) < 2:
                continue

            history_values = [f"{entry['date']} - {entry['price']:,}" for entry in relevant_price_history]
            price_history_string = "\n".join(history_values)

            last_price = relevant_price_history[-1]["price"]
            previous_price = relevant_price_history[-2]["price"]

            absolute_change = f"{last_price - previous_price:,}"
            percentage_change = round(100 * (last_price - previous_price) / previous_price, 2)

            last_change = f"{absolute_change} ({percentage_change} %)"

            data.append([info["info"], price_history_string, last_change, info["link_to_show"]])

        headers = ["info", "price_history", "last_change", "link"]
        table = tabulate(data, headers=headers, tablefmt='grid')
        print(table)

    def _get_sorted_by_last_change(self, field_of_change, flats):
        return sorted(flats, key=lambda flat: helpers.get_timestamp_from_formatted_date(
                      flat[field_of_change][-1]["date"]))

    def some_offer_state(self):
        results = self._get_results()
        key = "state_of_offer"
        flats_changed_offer = self._get_results_with_specific_key(results, key)
        for flat in flats_changed_offer:
            # self._print_basic_info(flat)
            print(flat["state_of_offer"])
            # self._print_horizontal_divide()

    def _changed_value_of(self, key):
        key_history = "{}_history".format(key)
        results = self._get_results()
        changed_flats = [result for result in results if key_history in result]

        return changed_flats

    def average_price(self):
        results = self._get_results()
        average_price = self._get_average_price(results)
        print("Average price", f"{average_price:,}")

        return average_price

    def _get_average_price(self, results):
        number_of_results = len(results)
        combined_price = sum([flat["price"] for flat in results])
        average_price = combined_price // number_of_results

        return average_price

    def median_price(self):
        results = self._get_results()
        median_price = self._get_median_price(results)
        print("Median price", f"{median_price:,}")

        return median_price

    def _get_median_price(self, results):
        prices = [flat["price"] for flat in results]
        number_of_prices = len(prices)
        price_sorted_results = sorted(prices)
        half_in_results = number_of_prices // 2
        median_price = price_sorted_results[half_in_results]

        return median_price

    @staticmethod
    def aggregate_all_possible_values(results, key):
        values = defaultdict(int)
        for result in results:
            value = result.get(key, "Unknown")
            values[value] += 1

        sorted_values = sorted(values.items(), key=lambda x: x[1], reverse=True)

        table = tabulate(sorted_values, headers=[key, 'Amount'], tablefmt='pretty')
        print(table)

    def amount_of_types(self):
        results = self._get_results()
        self.aggregate_all_possible_values(results, "type")

    def owning_state(self):
        results = self._get_results()
        self.aggregate_all_possible_values(results, "owning_state")

    def state_of_object(self):
        results = self._get_results()
        self.aggregate_all_possible_values(results, "state_of_object")

    def new_today(self):
        today_date = datetime.now().strftime('%Y-%m-%d')
        results = self._get_results()

        key = "first_seen_date"
        value = today_date

        matching_results = self._get_results_with_exact_key_value(results, key, value)

        self.show_all_information_in_a_table(matching_results)

        print("Flats new today:", len(matching_results))

        return matching_results

    def not_active_anymore(self):
        today_date = datetime.now().strftime('%Y-%m-%d')
        results = self._get_results()

        key = "last_update_date"
        value = today_date

        matching_results = self._get_results_with_different_key_value(results, key, value)

        print("Flats not active anymore:", len(matching_results))

        return matching_results

    def _get_results_with_specific_key(self, results, key):
        matching_results = [result for result in results if key in result]
        return matching_results

    def _get_results_with_exact_key_value(self, results, key, value):
        matching_results = [result for result in results if result.get(key) == value]
        return matching_results

    def _get_results_with_different_key_value(self, results, key, value):
        matching_results = [result for result in results if result.get(key) != value]
        return matching_results

    def show_flat_containing_some_text(self):
        text = input("Text: ")
        return self.flat_containing_some_text(text)

    def flat_containing_some_text(self, text):
        text_pattern = re.compile(r'{}'.format(text), re.IGNORECASE)
        results = self._get_results()
        matching_results = [result for result in results if text_pattern.search(str(result))]

        self.show_all_information_in_a_table(matching_results)

        print("matching_results", len(matching_results))
        return matching_results

    def show_all_information_in_a_table(self, results):
        data = []
        for flat in results:
            info = self._get_basic_info(flat)
            description = flat["description"]

            description = self.fit_text_into_column_with_character_limit(description, 60)
            link_to_show = self.fit_text_into_column_with_character_limit(info["link_to_show"], 610)

            new_info = [info["info"], info["price"], description, link_to_show]
            data.append(new_info)

        headers = ["info", "price", "description", "link"]
        table = tabulate(data, headers=headers, tablefmt='grid')
        print(table)

    @staticmethod
    def include_horizontal_delimiter(text):
        lines_lengths = [len(line) for line in text.splitlines()]
        max_line_length = max(lines_lengths)

        return text + "\n" + max_line_length*"-"

    @staticmethod
    def fit_text_into_column_with_character_limit(text, line_limit=60):
        new_lines = []
        lines = text.splitlines()
        for line in lines:
            while True:
                new_lines.append(line[:line_limit])
                if len(line) < line_limit:
                    break

                line = line[line_limit:]

        return "\n".join(new_lines)

    def show_specific_flat(self):
        flat_id = input("Flat ID: ")
        return self.get_specific_flat(flat_id)

    def get_specific_flat(self, flat_id):
        results = self._get_results()
        flats = self._get_results_with_exact_key_value(results, "flat_id", flat_id)

        if len(flats) < 1:
            print("Impossible to locate this ID")
        else:
            for key, value in flats[0].items():
                print(key, value)

        return flats

    def new_flats_each_day(self):
        results = self._get_results()
        self._aggregate_info_by_time(results, "first_seen_date")

    def sold_flats_each_day(self):
        results = self._get_results()
        self._aggregate_info_by_time(results, "last_update_date")

    def sold_last_week(self):
        results = self._get_results()

        utc_dt_object = datetime.now()
        day_start = datetime(
            year=utc_dt_object.year, month=utc_dt_object.month,
            day=utc_dt_object.day, hour=0, second=0)
        week_ago = day_start - timedelta(days=7)
        day_start_ts = day_start.timestamp()
        week_ago_ts = week_ago.timestamp()

        results = [result for result in results if result["last_update_ts"] > week_ago_ts]
        results = [result for result in results if result["last_update_ts"] < day_start_ts]

        sorted_flats = sorted(results, key=lambda flat: flat["last_update_ts"])

        data = []
        for flat in sorted_flats:
            basic_info = self._get_basic_info(flat)
            info = basic_info["info"]
            price = basic_info["price"]

            last_update = flat["last_update_date"]

            data.append([info, price, last_update])

        headers = ["info", "price", "last_update"]
        table = tabulate(data, headers=headers, tablefmt='grid')
        print(table)

        print("matching_results", len(results))

    def new_last_week(self):
        results = self._get_results()

        week_ago = datetime.now() - timedelta(days=7)
        week_ago_ts = week_ago.timestamp()

        results = [result for result in results if result["first_seen_ts"] > week_ago_ts]

        sorted_flats = sorted(results, key=lambda flat: flat["first_seen_ts"])

        data = []
        for flat in sorted_flats:
            basic_info = self._get_basic_info(flat)
            info = basic_info["info"]
            price = basic_info["price"]

            first_seen = flat["first_seen_date"]
            last_update = flat["last_update_date"]

            link = flat["link"]
            if last_update == helpers.get_current_date():
                link_to_show = link
            else:
                link_to_show = f"SOLD on {last_update}!"

            data.append([info, price, first_seen, link_to_show])

        headers = ["info", "price", "first_seen", "link"]
        table = tabulate(data, headers=headers, tablefmt='grid')
        print(table)

        print("matching_results", len(results))

    def _aggregate_info_by_time(self, results, key):
        days_and_values = defaultdict(int)
        for result in results:
            value = result[key]
            days_and_values[value] += 1

        sorted_by_time = sorted(days_and_values.items(),
            key=lambda x: helpers.get_timestamp_from_formatted_date(x[0]))

        table = tabulate(sorted_by_time, headers=['Day', key], tablefmt='pretty')
        print(table)

    def _get_basic_info(self, flat):
        type = flat["type"]
        area = flat.get("area_in_square_meters", 0)
        locality = flat["locality"]
        last_update = flat["last_update_date"]
        link = flat["link"]
        owning_state = flat.get("owning_state", "Unknown")
        state_of_object = flat.get("state_of_object", "Unknown")
        link = flat["link"]
        price = f"{flat['price']:,}"

        owning_part = "" if owning_state == "Osobní" else f" ({owning_state})"

        info = f"{type}, {area} m2, {state_of_object}{owning_part}\n{locality}"
        if last_update == helpers.get_current_date():
            link_to_show = link
        else:
            link_to_show = f"SOLD on {last_update}!"

        return {
            "info": info,
            "price": price,
            "link_to_show": link_to_show,
        }

    @staticmethod
    def _print_horizontal_divide():
        print(80*"*")


if __name__ == "__main__":
    statistics = Statistics()

    # (description, keyword, function)
    query_to_function = [
        ("Total amount of flats we have", "total", "overall_number_of_flats_we_have"),
        ("Flats changed prices recently", "changed_price", "display_details_of_changed_prices"),
        ("Some offer state", "offer_state", "some_offer_state"),
        ("Amount of specific types", "types", "amount_of_types"),
        ("Ownership types", "owning_state", "owning_state"),
        ("State of object types", "state_of_object", "state_of_object"),
        ("Average price", "average_price", "average_price"),
        ("Median price", "median_price", "median_price"),
        ("Flats new today", "new_today", "new_today"),
        ("Flats not active anymore", "not_active_anymore", "not_active_anymore"),
        ("Flats containing some text", "some_text", "show_flat_containing_some_text"),
        ("Show specific flat", "specific_id", "show_specific_flat"),
        ("New flats each day", "daily_new", "new_flats_each_day"),
        ("Sold each day", "daily_sold", "sold_flats_each_day"),
        ("Sold in the last week", "sold_last_week", "sold_last_week"),
        ("New in the last week", "new_last_week", "new_last_week"),
    ]

    # TODO: create querying logic like "today" "sold", etc. to filter any query

    def call_function_according_to_number_input(number):
        try:
            func = getattr(statistics, query_to_function[int(number)][-1])
            func()
        except IndexError as e:
            print("That index is not supported. Err:", e)
        except ValueError as e:
            print("Not an integer inputted. Err:", e)

    def call_function_according_to_string_input(string):
        # Looking for the right query and triggering that function
        for q_t_f in query_to_function:
            if string == q_t_f[1]:
                func = getattr(statistics, q_t_f[-1])
                func()
                break
        else:
            print("No argument like that - ", string)

    def show_all_possibilities():
        for index, q_t_f in enumerate(query_to_function):
            print(f"({index}) - {q_t_f[1]} - {q_t_f[0]}")

    if len(sys.argv) > 1:
        query = sys.argv[1]
        try:
            int(query)
            call_function_according_to_number_input(query)
        except ValueError:
            call_function_according_to_string_input(query)
    else:
        show_all_possibilities()

        number = input("Which one? ")
        statistics._print_horizontal_divide()
        call_function_according_to_number_input(number)
