"""
This script's purpose is to test the performance of python in analysing the
    big text file and counting the number of occurrences of each word.
The biggest takeaway from this is that printing to the console is
    waaaaaaaaaaaaaay slower than saving the results to a separate file.
There are two possibilities (at least), how to get individual words from
    a text - finding all the word-like sequences by regex, or splitting the
    text to chunks by a non-word characters.
    It turned out that both approaches are approximately of the same speed,
        there is a little advantage of the splitting solution (couple %).
"""

import re
import time


def main():
    # Comparing the two implementations after each other
    # Both measurements are an infinite loops, which have to be stopped
    #   after desired time by pressing Ctrl+C in the python console
    print("To abort the test, please press Ctrl+C, the next test in the row will start automatically.")
    measure_average_time(analyze_the_file_re_findall)
    measure_average_time(analyze_the_file_re_split)


def analyze_the_file_re_findall():
    word_count = {}
    pattern = re.compile(r"\w+")

    with open("text.txt", "r") as file:
        for line in file.readlines():
            matches = pattern.findall(line)
            include_words_from_array_to_dictionary(matches, word_count)

    process_the_resulting_dictionary(word_count)


def analyze_the_file_re_split():
    word_count = {}

    with open("text.txt", "r") as file:
        for line in file.readlines():
            matches = re.split("[ \n\r\t\.,!?:;\"\'\(\)\[\[\]\{\}] *", line)
            include_words_from_array_to_dictionary(matches, word_count)

    process_the_resulting_dictionary(word_count)


def include_words_from_array_to_dictionary(array, dictionary):
    """
    Helper function to include words from an array to the existing dictionary.
    I was not sure this will work, but it turns out it is possible to
        modify variables in place with functions like these, which is
        a pleasant thing and nice refactoring possibility.
    """
    for element in array:
        if element in dictionary:
            dictionary[element] += 1
        else:
            dictionary[element] = 1


def process_the_resulting_dictionary(dictionary):
    """
    Helper function to refactor all the common functionality for the
        processing of the result, which is same for every function.
    """
    # Saving the results to a file, which turned out to be a preferred
    #   method of storing this large output, much quicker than printing
    #   it to the console.
    # NOTE: even when the file is already filled from the previous attempt,
    #   it will be erased and written from the scratch
    with open("result.txt", "w") as new_file:
        for key in dictionary:
            new_file.write("Word: \"{}\" | count: {}\n".format(key, dictionary[key]))

    # Printing the results to the console, which has shown itself to be
    #   very ineffective and time-consuming
    # for key in dictionary:
    #     print("Word: \"{}\" | count: {}".format(key, dictionary[key]))


def measure_average_time(our_function):
    """
    Function to measure the average time it takes for a specific function to run.
    Its creation was inspired by the Law of large numbers, and a basic
        statistics, which says the more attempts we try, the more precise
        results will be yielded.
    Current implementation: The measurements are running indefinitely,
        until we manually stop the function by KeyboardInterrupt (Ctrl+C).
        It is important that the print statements are outside of the time
            difference, and therefore do not influence the function time,
            otherwise they would be causing an error in the measurement
    It would be quite straightforward to change this behaviour to some other,
        for example running the loop 10 times, or running it for a certain
        amount of time.
    """
    print("*"*80)
    print("We are testing \"{}\" function.".format(our_function.__name__))
    count = 0
    spent_time = 0

    try:
        while True:
            now = time.time()

            our_function()

            diff = time.time() - now
            print("This loop took {} seconds.".format(diff))

            count += 1
            spent_time += diff
    except KeyboardInterrupt:
        print("*"*80)
        print("End of the test for \"{}\" function".format(our_function.__name__))
        print("There were {} loops".format(count))
        print("The average loop time was {} seconds".format(spent_time/count))
        print("In one second it could run {} times".format(count/spent_time))
        print("*"*80)


if __name__ == "__main__":
    main()
