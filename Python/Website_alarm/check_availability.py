import os
import time
import traceback
import winsound

import pyautogui

WORKING_DIRECTORY = os.path.dirname(os.path.realpath(__file__))

picture_location = "kosik.png"
full_picture_location = os.path.join(WORKING_DIRECTORY, picture_location)

alarm_wav_location = "alarm.wav"
alarm_full_wav_location = os.path.join(WORKING_DIRECTORY, alarm_wav_location)

error_wav_location = "error.wav"
error_full_wav_location = os.path.join(WORKING_DIRECTORY, error_wav_location)


def is_there_a_kosik() -> bool:
    """
    Finds out if there is a kosik on the screen
    """

    # Trying to locate the picture on the screen and returning the result
    position_of_object = pyautogui.locateOnScreen(full_picture_location)
    print(position_of_object)
    return position_of_object is not None


def click_on_kosik() -> None:
    """
    Clicks on kosik to add stuff into it
    """

    # Finding out the coordination of kosik and clicking it
    position_of_object = pyautogui.locateOnScreen(full_picture_location)
    if position_of_object:
        center_of_object = pyautogui.center(position_of_object)  # type: ignore
        pyautogui.click(center_of_object)
        print("clicked on kosik!!!")


def refresh_the_page() -> None:
    """
    Refreshes the page
    Waiting for some time for the page to fully load before continuing
    """

    # hotkeys_to_press = ["ctrl", "f5"]
    hotkeys_to_press = ["f5"]
    pyautogui.hotkey(*hotkeys_to_press)
    time.sleep(5)
    print("done refreshing")


def success_action() -> None:
    """
    Defines what to do when we locate the kosik
    """

    print("SUCCESS")

    # Click on it
    click_on_kosik()

    # Playing the defined sound (make it loud!!!!!!!!)
    for _ in range(20):
        winsound.PlaySound(alarm_full_wav_location, winsound.SND_FILENAME)


def handle_error() -> None:
    """
    Defines what to do when we encounter some unexpected error
    """

    print("ERROR")
    # Playing the defined sound (make it loud!!!!!!!!)
    for _ in range(20):
        winsound.PlaySound(error_full_wav_location, winsound.SND_FILENAME)


if __name__ == "__main__":
    # Having an infinite loop of trying to locate kosik, and handling all
    #   the unexpected errors by triggerring error action
    while True:
        try:
            time.sleep(3)
            refresh_the_page()
            result = is_there_a_kosik()
            if result:
                success_action()
                break
        except Exception as err:
            print(err)
            print(traceback.format_exc())
            handle_error()
