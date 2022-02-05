import os
import json

WORKING_DIRECTORY = os.path.dirname(os.path.realpath(__file__))

db_file_path = "db.json"
db_file_path = os.path.join(WORKING_DIRECTORY, db_file_path)

if not os.path.exists(db_file_path):
    with open(db_file_path, "w") as my_file:
        my_file.write("{}")


def get_results():
    return read_the_db()


def process_post(request_data):
    key_to_save = request_data.get("key_to_save", "general")
    data = request_data.get("data", "hello_world")

    append_new_data_to_db(key_to_save, data)


def read_the_db():
    with open(db_file_path, "r", encoding="utf-8") as my_file:
        results = json.load(my_file)
        return results


def save_new_results_to_db(new_results):
    with open(db_file_path, "w", encoding="utf-8") as my_file:
        json.dump(new_results, my_file, indent=4, ensure_ascii=False)


def append_new_data_to_db(key_to_save, data):
    results = read_the_db()
    if key_to_save in results:
        results[key_to_save].append(data)
    else:
        results[key_to_save] = [data]

    save_new_results_to_db(results)
