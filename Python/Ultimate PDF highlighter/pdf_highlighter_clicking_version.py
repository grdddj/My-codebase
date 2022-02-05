"""
This script is automatically highlighting text in a PDF document,
    as well as storing the text in a clipboard.
It was developed for Adobe Acrobat Reader DC, version 2019
It is listening for clicks with middle mouse button,
    and is triggering action when it registers it.

It is invaluable in combination with clipboard monitoring script.
The combination of those two will handle everything from highlighting
    the chosen text with a colour, processing the PDF text and saving it
    to a file.
All what is needed is to choose the text you really like by highlighting it
    with a mouse, and pressing the middle mouse button (wheel).
Weee, automation!!!!!!!!!!!!!!!

If you have another screen resolution than 1920*1080, you will
    also need to make a screenshot of the PDF "highlight" button,
    for python to be able to recognize it on the screen.

NOTE: there can be issues with recognizing the highlighting button when
    we have multiple monitors, as each monitor can have different
    resolution, and therefore the button will not be recognized
    pixel-wise.
NOTE2: There is also a problem with multiple monitors that pyautogui is
    examining only the main one (in my case the laptop monitor).

I am also experimenting here with static type-checking in python.
Needed steps to perform this validation:
- pip install mypy
- mypy script.py
- it can happen (and it happens now), that it will find errors, because the
    imported libraries do not incorporate types
Very nice articles about type-checking in python ca be found here:
- https://realpython.com/python-type-checking/
- https://medium.com/@ageitgey/learn-how-to-use-static-type-checking-in-python-3-6-in-10-minutes-12c86d72677b

The final thing is that I have just started using virtual environments
    in python, so I am enclosing a requirements.txt file for everybody.
Super article about it:
- https://medium.com/@boscacci/why-and-how-to-make-a-requirements-txt-f329c685181e
One strange thing I noticed is the script is reacting much more slowly
    when executed inside the virtual environment
    (taking longer time to recognize the button and click it)
"""

import logging
import subprocess
import time

import pyautogui
from helpers import Helpers
from pynput import mouse

# Using logging as a neat way to find out errors in production
ERROR_FILENAME = "pdf_highlighter_clicking_ERRORS.log"
logging.basicConfig(
    filename=ERROR_FILENAME,
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

# Full path to the Notepad executable, to be able to open error logs in it
NOTEPAD_PATH = r"C:\Windows\notepad.exe"


class Global:
    # Specifying which mouse clicks to listen for, where is the picture
    #   we want to be clicking, and which keyboard action we want to take
    mouse_button_to_listen = mouse.Button.middle
    where_to_click_picture_location = "highlight_button.png"
    hotkeys_to_press = ["ctrl", "c"]

    # Defines the size of the square around cursor that button will
    #   be located at first, to speed up the process
    # The lower this value, the quicker the identification process,
    #   however when too small, it does not have to find it inside
    #   this small area, which will make the search take longer time
    square_size_where_to_look_for_button_first = 500

    # How similar must the object be to our template to be considered the same
    # Is accounting for some small colour-differences
    confidence_of_locating = 0.9

    # Storing how many times the function was used
    amount_of_usage = 0

    # Whether to show user notifications
    SHOW_NOTIFICATIONS = False

    # Instruction for the user that will be shown at the beginning
    start_instructions = """
    This program is making PDF color highlighting and data copying a breeze.

    Just highlight the wanted text in PDF and click on it with a
    middle mouse button.
    Program will press Ctrl+C for you, to put data into clipboard,
    as well as click the highlighter button.

    Already got everything highlighted and processed?
    Click with middle mouse button on the very top of the screen.
    """

    # Template for the message that will be shown after user ends the script
    end_summary_template = (
        "Thank you for using the service!\n\nYou have used the function {} times!"
    )


def on_click(x_coord: int, y_coord: int, button, pressed: bool) -> bool:
    """
    What should happen when a click event is registered
    Listening on release of the button - not on press, because pressed
        middle button is causing confusion to the mouse
        (and generally it is a good idea to listen on release, as the
        release itself then does not cause some unexpectancies)
    """

    # Contacting stop function with the same parameters,
    #   and if it decides we should stop, then stop by returning False
    if stop_listening(x_coord, y_coord, button, pressed):
        if Global.SHOW_NOTIFICATIONS:
            pyautogui.alert(
                text=Global.end_summary_template.format(Global.amount_of_usage),
                title="SEE YOU SOON!",
                button="OK",
            )

        return False

    # If the specified mouse button is released, trigger the main action
    if button == Global.mouse_button_to_listen and not pressed:
        copy_and_highlight()

    return True


def stop_listening(x_coord: int, y_coord: int, button, pressed: bool) -> bool:
    """
    Condition for which to stop listening (finish the script)
    Has the same arguments as on_click(), and can be arbitrary tuned
    """

    # Return True when we click with the mouse on the very top of the screen
    # It is again beneficial to listen on the release (and not press),
    #   because release of the middle button causes havoc
    if y_coord == 0 and button == Global.mouse_button_to_listen and not pressed:
        return True

    return False


def copy_and_highlight() -> None:
    """
    Responsible for pressing configured keys and clicking certain
        location on the screen, according to supplied picture
    From observation it takes around 0.5 seconds to locate it and click it
    """

    # Sleeping to wait for proper release of the middle button
    time.sleep(0.1)

    # Pressing the configured keys
    pyautogui.hotkey(*Global.hotkeys_to_press)

    # Saving current mouse position to navigate it back afterwards
    x_coord_original, y_coord_original = pyautogui.position()

    # Defining dictionary to improve the lookup speed of the button
    coords_and_square_size = {
        "x_coord": x_coord_original,
        "y_coord": y_coord_original,
        "square_size": Global.square_size_where_to_look_for_button_first,
    }

    # Trying to locate the object on the current screen
    position_of_object = Helpers._get_position_of_object(
        object_image_location=Global.where_to_click_picture_location,
        confidence_of_locating=Global.confidence_of_locating,
        coords_and_square_size=coords_and_square_size,
    )

    # If we receive valid answer, click at the center of the object
    #   and then move the mouse back to its original location
    if position_of_object["found"]:
        center_of_object = pyautogui.center(position_of_object["coords"])
        pyautogui.click(center_of_object)
        pyautogui.moveTo(x_coord_original, y_coord_original)

        # Increasing the amount of usages of this function
        Global.amount_of_usage += 1
        print("Object clicked")
    else:
        print("OBJECT NOT LOCATED!!!")


if __name__ == "__main__":
    try:
        # Notifying the user and starting to listen
        if Global.SHOW_NOTIFICATIONS:
            pyautogui.alert(
                text=Global.start_instructions,
                title="PDF HIGLIGHTER - INSTRUCTIONS",
                button="OK",
            )
        print(Global.start_instructions)
        print(
            "\nWARNING!\nThere needs to be a file 'highlight_button.png'"
            + "the picture of the highlighting button!"
        )
        with mouse.Listener(on_click=on_click) as listener:
            listener.join()
    except Exception as e:
        # If some unexpected exception happens, log it and encourage user to
        #   look there, and maybe report the issue
        logging.exception(e)

        # Showing that there was some unexpected error
        error_text = "Exception ocurred - please look into the error log: {}".format(
            ERROR_FILENAME
        )
        print(error_text)

        pyautogui.alert(
            text=error_text, title="ERROR HAPPENED!", button="I will look there"
        )

        # Showing the error log in the Notepad
        # There can be multiple errors, like notepad path not existing etc.
        try:
            subprocess.Popen([NOTEPAD_PATH, ERROR_FILENAME])
        except:
            print("UNABLE TO LAUNCH NOTEPAD IN LOCATION '{}'".format(NOTEPAD_PATH))

        # Raising the actual error, to be also visible in the terminal
        raise (e)
