from pynput import keyboard
import os

file_dir = os.path.dirname(os.path.realpath(__file__))


class Config:
    # Stockfish engine downloaded at https://stockfishchess.org/download/
    engine_location = os.path.join(file_dir, "stockfish_13_win_x64_bmi2")
    time_limit_to_think = 0.2
    sleep_interval_between_screenshots = 0.1

    wait_for_keyboard_trigger_to_play = False
    keyboard_trigger = keyboard.Key.alt_r

    ###########################################
    # PART ABOUT THE COORDINATES
    ###########################################

    # Default state when coordiantes are unknown
    left_top = None
    right_bottom = None

    # https://lichess.org/analysis/standard
    website = "lichess"
    left_top = (563, 232)
    right_bottom = (1218, 890)
    white_field_highlight_colour = (205, 210, 106)
    black_field_highlight_colour = (170, 162, 58)

    # https://www.chess.com/cs/analysis
    # website = "chess.com"
    # left_top = (364, 178)
    # right_bottom = (1192, 1005)
    # white_field_highlight_colour = (247, 247, 105)
    # black_field_highlight_colour = (187, 203, 43)

    # https://www.chess.com/cs/play/computer
    # website = "chess.com"
    # left_top = (430, 243)
    # right_bottom = (1114, 921)
    # white_field_highlight_colour = (247, 247, 105)
    # black_field_highlight_colour = (187, 203, 43)

    # https://www.playok.com/cs/sachy/
    # website = "kurnik"
    # left_top = (425, 208)
    # right_bottom = (1108, 889)
    # white_field_highlight_colour = (47, 66, 45)
    # black_field_highlight_colour = (17, 53, 20)
