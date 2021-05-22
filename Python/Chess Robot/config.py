from pynput import keyboard
import os

file_dir = os.path.dirname(os.path.realpath(__file__))


class Config:
    # Stockfish engine downloaded at https://stockfishchess.org/download/
    engine_location = os.path.join(file_dir, "stockfish_13_win_x64_bmi2")

    # How many seconds to analyze before suggesting a move
    time_limit_to_think_normal = 0.3
    time_limit_to_think_when_already_winning = 0.05
    time_limit_to_think_when_losing = 1

    # When to consider we are winning or losing (to adjust think time)
    pawn_threshold_when_already_winning = 5
    pawn_threshold_when_losing = -0.5

    # How long to pause between watching again at the chessboard
    sleep_interval_between_screenshots = 0.1

    # Allowing for keyboard-triggered moves (instead of automatic)
    wait_for_keyboard_trigger_to_play = False
    keyboard_trigger = keyboard.Key.alt_r

    ###########################################
    # PART ABOUT THE COORDINATES AND COLOURS
    ###########################################

    # https://lichess.org/analysis/standard
    website = "lichess"
    chessboard_left_top_pixel = (563, 232)
    chessboard_right_bottom_pixel = (1218, 890)
    white_field_highlight_colour = (205, 210, 106)
    black_field_highlight_colour = (170, 162, 58)

    # https://www.chess.com/cs/analysis
    # website = "chess.com"
    # chessboard_left_top_pixel = (364, 178)
    # chessboard_right_bottom_pixel = (1192, 1005)
    # white_field_highlight_colour = (247, 247, 105)
    # black_field_highlight_colour = (187, 203, 43)

    # https://www.chess.com/cs/play/computer
    # website = "chess.com"
    # chessboard_left_top_pixel = (430, 243)
    # chessboard_right_bottom_pixel = (1114, 921)
    # white_field_highlight_colour = (247, 247, 105)
    # black_field_highlight_colour = (187, 203, 43)

    # https://www.playok.com/cs/sachy/
    # website = "kurnik"
    # chessboard_left_top_pixel = (425, 208)
    # chessboard_right_bottom_pixel = (1108, 889)
    # white_field_highlight_colour = (47, 66, 45)
    # black_field_highlight_colour = (17, 53, 20)
