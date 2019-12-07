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
import pyautogui
import time
import logging
import subprocess

# Using logging as a neat way to find out errors in production
ERROR_FILENAME = "clipboard_monitor_ERRORS.log"
logging.basicConfig(filename=ERROR_FILENAME,
					level=logging.INFO,
					format='%(asctime)s %(levelname)s %(message)s')

# Full path to the Notepad executable, to be able to open error logs in it
NOTEPAD_PATH = r"C:\Windows\notepad.exe"

# To which file to save the results - default one and actual one to be used
SAVING_FILE_DEFAULT = "save.txt"
SAVING_FILE = ""

# Whether to embrace all the copied text by quotes in the saving file
EMBRACE_BY_QUOTES = True

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
    # Not writing to a file when value is empty for some reason
    if processed_value:
        with open(SAVING_FILE, "a") as content_file:
            if EMBRACE_BY_QUOTES:
                content_to_write = '"{}"\n'.format(processed_value)
            else:
                content_to_write = '{}\n'.format(processed_value)
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
    try:
        welcome_text = "Welcome to the clipboard monitoring script!\n\n" + \
            "Press CTRL+C in terminal to terminate the script.\n\n" + \
            "Press CTRL+C anywhere else, and the content in clipboard will " + \
            "be processed and saved into a file.\n"

        print(welcome_text)

        # Determining the filename to which save the results
        input_text = "Please choose the filename into which to save the results.\n" + \
                     "If no extension is specified, we will assume '.txt' file."
        SAVING_FILE = pyautogui.prompt(
                    text=welcome_text + "\n" + input_text,
                    title='WELCOME! + Filename input',
                    default=SAVING_FILE_DEFAULT)

        # If user clicks "Cancel", None will be send as a response, so assign
        #   the default one.
        # Otherwise strip whitespace (which cannot be done on None)
        if not SAVING_FILE:
            SAVING_FILE = SAVING_FILE_DEFAULT
        else:
            SAVING_FILE = SAVING_FILE.strip()

        # Including .txt extension if it was not specified
        if not "." in SAVING_FILE:
            SAVING_FILE = SAVING_FILE + ".txt"

        print("Fair enough, all the text you copy will be visible in ---'{}'---!".format(SAVING_FILE))

        # Determining if user wants to include quotes around the copied text
        quotes_text = "Do you want the copied text to be embraced by quotes to \"signal copying\"?"
        include_quotes = pyautogui.confirm(text=quotes_text,
                                           title='Should we include quotes?',
                                           buttons=['Yes', 'No'])
        EMBRACE_BY_QUOTES = include_quotes == "Yes"

        print("Fair enough, all the text you copy will{} be embraced by qoutes!".format(
            "" if EMBRACE_BY_QUOTES else " not"))

        print("\nListening for the clipboard changes....\n")

        # Starting the monitoring
        clipboard_checking_loop()
    except KeyboardInterrupt:
        # Pressing Ctrl+C in the terminal should result in gracefull termination
        print("Thanks for using this service!")
    except Exception as e:
        # If some unexpected exception happens, log it and encourage user to
        #   look there, and maybe report the issue
        logging.exception(e)

        # Showing that there was some unexpected error
        error_text = "Exception ocurred - please look into the error log: {}".format(ERROR_FILENAME)
        print(error_text)
        pyautogui.alert(
            text=error_text,
            title='ERROR HAPPENED!',
            button='I will look there')

        # Showing the error log in the Notepad
        # There can be multiple errors, like notepad path not existing etc.
        try:
            subprocess.Popen([NOTEPAD_PATH, ERROR_FILENAME])
        except:
            print("UNABLE TO LAUNCH NOTEPAD IN LOCATION '{}'".notepad(NOTEPAD_PATH))

        # Raising the actual error, to be also visible in the terminal
        raise(e)
