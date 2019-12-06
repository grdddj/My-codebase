"""
This script is automatically highlighting text in a PDF document,
    as well as storing the text in a clipboard.
It was developed for Adobe Acrobat Reader DC, version 2019
It is listening for a certain key (right Control),
    and is triggering action when it registers it.
The whole action takes around 0.5 seconds, and when the mouse travels
    to click somewhere, you get the sensation of magic!

It is invaluable in combination with clipboard monitoring script.
The combination of those two will handle everything from highlighting
    the chosen text with a colour, processing the PDF text and saving it
    to a file.
All what is needed is to choose the text you really like by highlighting it
    with a mouse, and pressing the right Control.
Weee, automation!!!!!!!!!!!!!!!

NOTE: You can improve the speed of highlighting by having your mouse
    close or even better over the highlighted area when triggering action -
    so the script does not have to locate the right spot where to click.

I am also experimenting here with static type-checking in python.
Needed steps to perform this validation:
- pip install mypy
- mypy script.py
- it can happen (and it happens now), that it will find errors, because the
    imported libraries do not incorporate types
Very nice articles about type-checking in python can be found here:
- https://realpython.com/python-type-checking/
- https://medium.com/@ageitgey/learn-how-to-use-static-type-checking-in-python-3-6-in-10-minutes-12c86d72677b

The final thing is that I have just started using virtual environments
    in python, so I am enclosing a requirements.txt file for everybody.
Super article about it:
- https://medium.com/@boscacci/why-and-how-to-make-a-requirements-txt-f329c685181e

Possible improvements:
- incorporating sounds - when it succeeds or fails, play some nice melody :)
"""

from pynput.keyboard import Key, Listener
import pyautogui

from helpers import Helpers

class Global:
    # Specifying which key to listen for, key for stopping,
    #   and which keyboard action we want to take
    key_to_action = Key.ctrl_r
    key_to_stop = Key.esc
    hotkeys_to_press = ["ctrl", "c"]

    # Whether to first explore where to click, not to cause some
    #   unexpected action
    # If set to True, we will only click on below-specified background
    VALIDATE_BEFORE_CLICKING = True

    # Specifying the colour of the highlighted background, to enable
    #   validating whether we are clicking on the right place
    pdf_mouse_highlighting_colour = (153, 193, 218)

    # Defines the size of the square around cursor that highlight colour will
    #   be located at first, to speed up the process
    # The lower this value, the quicker the identification process,
    #   however when too small, it does not have to find it inside
    #   this small area, which will make the search take longer time
    square_size_where_to_look_for_highlight_first = 500

    # Defines the grid-size (step) in pixels that the y-axis will be sliced
    #   into when searching on the screen for a highlighted area
    # The bigger it is, the quicker the locating can be, but there can be
    #   a danger of missing small (one-letter) highlights when having it
    #   over 15-20 pixels
    # When we analyze the whole picture, we are gradually dividing this by
    #   two if we are not successful - so finally we should find everything
    grid_size_when_searching = 10

    # Defines how many pixels we should ideally skip after we locate
    #   the background where to click
    # EXPLANATION: When there is already some highlighted text between
    #   the newly highlighted text and the direction we are approaching this,
    #   the already highlighted one is activated when we click on the
    #   very margin - and we do not want that
    # Therefore we will continue for couple pixels in the same direction
    #   before searching again, and hopefully click there
    pixels_to_skip_on_margin_if_possible = 10

    # Storing the information about the last key pressed, to be able to
    #   recognize pressing the stopping key two times in a row
    last_key_pressed = None

    # Storing how many times the function was used
    amount_of_usage = 0

    # Whether to show user notifications
    # NOTE: at first I had these notifications in the form of opening
    #   a Notepad with a file where the wanted text was written
    #   (and deleting the file right after it was opened).
    # Only then I discovered these Javascript-like alerts and other
    #   possibilities pyautogui offers.
    # The "Notepad notifications" have however one advantage - user can
    #   both read the notifications and use the program, while here the
    #   open alert blocks the program itself - and user has to close it.
    SHOW_NOTIFICATIONS = False

    # Instruction for the user that will be shown at the beginning
    start_instructions = \
    """
    This program is making PDF color highlighting and data copying a breeze.

    Just highlight the wanted text in PDF and press right Control.
    Program will press Ctrl+C for you, to put data into clipboard,
    as well as colourfully highlight the text in PDF.

    Already got everything highlighted and processed?
    Press Escape key two times in a row to terminate the program.
    """

    # Template for the message that will be shown after user ends the script
    end_summary = "" + \
        "Thank you for using the service!\n\n" + \
        "You have used the function {} times!"

def on_release(key) -> bool:
    """
    What should happen when a key is released
    Listening on release of the button - not on press, to prevent
        overload when the key would be pressed for a long time
        (there can be multiple on_press events, but only one on_release)
    """

    # Contacting stop function with the same parameters,
    #   and if it decides we should stop, then stop by returning False
    if stop_listening(key):
        if Global.SHOW_NOTIFICATIONS:
            pyautogui.alert(
                text=Global.end_summary.format(Global.amount_of_usage),
                title='SEE YOU SOON!',
                button='OK')

        return False

    # If the right key is released, trigger the main action
    if key == Global.key_to_action:
        copy_and_highlight()

    return True

def stop_listening(key) -> bool:
    """
    Condition for which to stop listening (finish the script)
    """

    # Return True when we press our stop key two times in a row
    if key == Global.key_to_stop and Global.last_key_pressed == Global.key_to_stop:
        return True

    Global.last_key_pressed = key
    return False

def copy_and_highlight() -> None:
    """
    Responsible for pressing configured keys and performing
        other logic to highlight the text
    """

    # Increasing the amount of usages of this function
    Global.amount_of_usage += 1

    # If we chose to validate the place we click, perform the validation
    if Global.VALIDATE_BEFORE_CLICKING:
        # Gathering information for the scree analysis
        x_coord_original, y_coord_original = pyautogui.position()
        my_screen = pyautogui.screenshot()

        # Contacting the helper function which will search for the
        #   right place where to click
        where_should_i_click = Helpers._locate_pixel_in_the_image(
            PIL_image=my_screen,
            colour_to_match=Global.pdf_mouse_highlighting_colour,
            x_coord=x_coord_original,
            y_coord=y_coord_original,
            square_size=Global.square_size_where_to_look_for_highlight_first,
            pixels_to_skip_on_margin_if_possible=Global.pixels_to_skip_on_margin_if_possible,
            grid_size_when_searching=Global.grid_size_when_searching)

        # Performing the action only when we received positive results
        # Because the mouse could have to move to click, move it to its original
        #   position afterwards (also to show the user which powers we have)
        if where_should_i_click["should_i_click"]:
            assert(my_screen.getpixel(where_should_i_click["coords"]) == Global.pdf_mouse_highlighting_colour)
            pyautogui.hotkey(*Global.hotkeys_to_press)
            pyautogui.click(*where_should_i_click["coords"], button="right")
            pyautogui.typewrite("z")
            pyautogui.moveTo(x_coord_original, y_coord_original)
    # If the validation is not chosen, just clicking at the current spot
    #   and hope it will trigger wanted action
    else:
        # Pressing the configured keys
        pyautogui.hotkey(*Global.hotkeys_to_press)

        # Pressing right mouse button and then "z" letter, which causes the
        #   highlighted text to be coloured
        pyautogui.click(button="right")
        pyautogui.typewrite("z")

if __name__ == "__main__":
    # Notifying the user and starting to listen
    if Global.SHOW_NOTIFICATIONS:
        pyautogui.alert(
            text=Global.start_instructions,
            title='PDF HIGLIGHTER - INSTRUCTIONS',
            button='OK')
    print(Global.start_instructions)
    with Listener(on_release=on_release) as listener:
        listener.join()
