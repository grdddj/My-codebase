"""
This script is attempting to analyse data files containing experimental
    data from piping experiments.
It was written after despair of analyzing the data manually in MS Excel

It offers quick and programmable way of getting mean averages of columns
    from a data file
"""

import os
import glob

# Defining common data for all the files
FILE_EXTENSION = "lvm"
DELIMITER = "\t"
QUANTITIES_LINE_IDENTIFIER = "X_Value"
UNIT_LINE_IDENTIFIER = "Y_Unit_Label"
EXPECTED_NUMBER_OF_LINES = 60000
RESULTS_FILE = "results.txt"


def get_all_files_with_given_extension(extension):
    """
    Returning all files with a given extension from the same directory as the script
    """

    path_of_the_file = os.path.dirname(os.path.realpath(__file__))
    all_files = glob.glob(os.path.join(path_of_the_file, "*.{}".format(extension)))
    return all_files


def line_contains_valid_experiment_data(line):
    """
    Determining whether the data contains valid data to be analysed
    It is valid when the first "column" is parseable to a float (decimal number)
        - because the first column should be a time value
    """

    delimited_info = line.strip().split(DELIMITER)
    try:
        float(delimited_info[0])
    except ValueError:
        return False

    return True


def convert_list_from_string_to_float(list_of_values):
    """
    Converts all the values from a text to a decimal number
    If not possible, notify about it, as it can mean a problem is there,
        and input a zero value there
    Error is propagated higher, when it is also handled
    NOTE: because of the possible errors when parsing, we need to use
        this rather long function instead of elegant list comprehension
        - new_values = [float(value) for value in old_values]
    """

    list_of_numbers = []
    errors = []
    for value in list_of_values:
        try:
            new_value = float(value)
        except ValueError:
            new_value = 0
            error = "WARNING: impossible to parse a number: '{}'".format(value)
            print(error)
            errors.append(error)

        list_of_numbers.append(new_value)

    return (list_of_numbers, errors)


def process_a_file(file_name):
    """
    Analyses the data in a single file
    """

    # Opening the given file and analyzing it line by line
    with open(file_name, "r") as my_file:
        print("file_name", file_name)

        units = []
        quantities = []
        values = []
        errors = []
        for line in my_file.readlines():
            # Saving the real experiment data
            if line_contains_valid_experiment_data(line):
                # Extracting the individual data and converting them to numbers
                delimited_info_in_text = line.strip().split(DELIMITER)
                delimited_info_in_numbers, error = convert_list_from_string_to_float(
                    delimited_info_in_text)
                values.append(delimited_info_in_numbers)

                # Logging the errors that may happen during the conversion
                if error:
                    errors.append(error)

            # Saving the units (kPa, C, Nm...)
            elif line.startswith(UNIT_LINE_IDENTIFIER):
                units = line.strip().split(DELIMITER)

            # Saving the quantities (p1, Q, t...)
            elif line.startswith(QUANTITIES_LINE_IDENTIFIER):
                quantities = line.strip().split(DELIMITER)

        # Calculating the mean value in all the columns
        # We did not want to use numpy, so that script can run without libraries
        # https://stackoverflow.com/questions/15819980/calculate-mean-across-dimension-in-a-2d-array
        mean_values = [float(sum(l))/len(l) for l in zip(*values)]

        # Aggregating the results and saving them into a text file
        # The content is being appended, so the old data in a file will persist
        with open(RESULTS_FILE, "a") as results_file:
            results_file.write("file_name: {}\n".format(file_name))

            # Validating if all the lines were parsed correctly and showing errors
            results_file.write("number of expected lines: {}\n".format(EXPECTED_NUMBER_OF_LINES))
            results_file.write("number of valid lines: {}\n".format(len(values)))
            if len(values) < EXPECTED_NUMBER_OF_LINES:
                results_file.write(80*"x" + "\nWARNING: NOT ALL OF THE LINES WERE CORRECTLY PARSED!!\n")
            if len(errors) > 0:
                results_file.write("{}\n{}\n{}\n".format(80*"x", str(errors), 80*"x"))

            # Writing the real results - mean values
            for quantity, mean_value, unit in zip(quantities, mean_values, units):
                result = "Mean of {} [{}] = {}".format(quantity, unit, mean_value)
                results_file.write(result + "\n")
                print(result)

            results_file.write(80*"*" + "\n")


if __name__ == "__main__":
    # Getting the list of all data files and processing them
    files = get_all_files_with_given_extension(FILE_EXTENSION)
    for file in files:
        process_a_file(file)
