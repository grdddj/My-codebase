"""
This script is monitoring clipboard for new values, and can
    then perform arbitrary logic with these values.
Currently it is getting rid of all newlines, and
    is saving the one-line output to the file.

Other possible use-cases:
- real-time translation of the text in clipboard (copy Czech, paste English)
- keeping track of all the values in clipboard (for personal or spying purposes)
"""

import pyperclip
import time

# To which file to save the results
SAVING_FILE = "save.txt"

# How frequently to check the clipboard
CHECK_PERIOD_IN_SECONDS = 0.1

def process_the_value(value_from_clipboard):
    """
    Defining what should happen with the new value that is found in
        the clipboard.
    Returns the processed value
    """
    # Getting rid of all the returns and newlines, to preserve only one line
    processed_value = value_from_clipboard.strip()
    processed_value = processed_value.replace("\r", " ")
    processed_value = processed_value.replace("\n", " ")
    processed_value = processed_value.replace("  ", " ")

    # Appending the new text to a file, embraced by qoutes, to signal
    #   it was copied
    with open(SAVING_FILE, "a") as content_file:
        content_to_write = '"{}"\n'.format(processed_value)
        content_file.write(content_to_write)

    return processed_value

def clipboard_checking_loop():
    """
    Loop constantly checking the clipboard for new values.
    If it encounters new value, it will supply this value to
        processing function.
    It will also store a new value to the clipboard, according
        to the output of the processing function.
    """
    current_clipboard_content = pyperclip.paste()

    while True:
        time.sleep(CHECK_PERIOD_IN_SECONDS)

        new_clipboard_content = pyperclip.paste()

        # If the clipboard content changed from the previous loop, do something
        if new_clipboard_content != current_clipboard_content:
            # Getting the transformed content, and saving it to the clipboard
            new_content = process_the_value(new_clipboard_content)
            pyperclip.copy(new_content)
            current_clipboard_content = new_content
            print("Value processed and saved!")


if __name__ == "__main__":
    print("Welcome to the clipboard monitoring script!")
    print("Press CTRL+C here in terminal to terminate the script.")
    print("Press CTRL+C anywhere else, and the content in clipboard will " + \
          "be processed and saved into a file.")
    try:
        clipboard_checking_loop()
    except KeyboardInterrupt:
        print("Thanks for using this service!")
