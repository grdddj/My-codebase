import all_flats


def delete_last_edit_history():
    results = all_flats.get_last_results()
    for flat_id in results:
        results[flat_id].pop("last_edit_history", None)

    all_flats.save_new_results(results)


if __name__ == "__main__":
    all_flats.archive_last_results()
    delete_last_edit_history()
