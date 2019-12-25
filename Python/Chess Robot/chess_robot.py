"""
This script is playing chess without any human intervention (almost).
Just define the coordination of the chessboard and some identificator
    of the oponent moves, and it is ready to beat even the strongest
    grandmasters!
Is tuned for websites chess.com and playok.com, but can be relatively easily
    upgraded to handle almost any chessboard.

Possible improvements:
- having it more modular instead of one script
- handling of promotion via image recognition

- wait for some variable time before making a move, not to look suspicious
- listen for certain keys when being turned on and off, so we do not have
    to leave the mouse from playing window (which is visible to oponent)
- having a command key that would issue the move (press it, move) - and
    wait for this before moving, to create authentic play (fast and slow)
"""

import pyautogui
from pynput import mouse
import time

# Documentation here: https://python-chess.readthedocs.io/en/latest/
import chess
import chess.engine

# Initializing the chessboard
# Downloading stockfish engine at https://stockfishchess.org/download/
board = chess.Board()
engine = chess.engine.SimpleEngine.popen_uci("D:\stockfish-10-win\Windows\stockfish_10_x64")
limit = chess.engine.Limit(time=0.2)

# Getting the colour user will be playing with
print("Please move the console to a second screen")
our_colour = input("Choose the colour: ")
if our_colour and our_colour[0] == "b":
    our_colour = "black"
else:
    our_colour = "white"
print("You chose {} pieces, good luck in the game!".format(our_colour))

# Defining helper methods for this file
class HelpersToAssignChessboard:
    def stop_listening():
        global left_top, right_bottom
        if left_top is not None and right_bottom is not None:
            print("stopping the assignment")
            return True
        return False

    def on_click(x, y, button, pressed):
        global left_top, right_bottom
        if HelpersToAssignChessboard.stop_listening():
            return False
        if button == mouse.Button.right and pressed:
            if left_top is None:
                left_top = (x, y)
                print("left_top assigned - {},{}".format(x, y))
                print("Please rightlick the most bottomright corner of the chessboard")
            elif right_bottom is None:
                right_bottom = (x, y)
                print("right_bottom assigned - {},{}".format(x, y))

    def create_dict_of_square_centers(left_top, right_bottom, our_colour):
        board_size = right_bottom[0] - left_top[0]
        square_size = board_size // 8

        # Constructing the dictionary of square centers
        # We must distinguish between playing white or black when doing that
        rows = "12345678"
        columns = "abcdefgh"
        square_centers = {}

        for col_index, col in enumerate(columns):
            for row_index, row in enumerate(rows):
                coord = col + row
                if our_colour == "white":
                    center_x = left_top[0] + (square_size // 2 + col_index * square_size)
                    center_y = right_bottom[1] - (square_size // 2 + row_index * square_size)
                else:
                    center_x = right_bottom[0] - (square_size // 2 + col_index * square_size)
                    center_y = left_top[1] + (square_size // 2 + row_index * square_size)
                square_centers[coord] = (center_x, center_y)

        return square_centers

class HelpersToAnalyzeChessboard:
    def are_there_colours_in_a_PIL_image(PIL_image,
                                           colours_to_locate: list) -> dict:
        # Getting the list of all colours in that image
        ocurrences_and_colours = PIL_image.getcolors(maxcolors=66666)

        # Trying to locate our wanted colour there
        for ocurrence, colour in ocurrences_and_colours:
            if colour in colours_to_locate:
                return {"is_there": True, "ocurrences": ocurrence}
        else:
            return {"is_there": False, "ocurrences": None}

    def get_highlighted_squares_from_picture(whole_screen, square_centers, square_size, highlighted_colours):
        highlighted_squares = []

        # Defining how big part of a square will be cut out to allow for some
        #   inacurracies in square identification (so that the highlighted
        #   colours are really found only on two squares)
        square_boundary = 0.1
        square_boundary_pixels = square_size * square_boundary

        # Looping through all squares, and testing if they contain highlighted
        #   colour
        for key, value in square_centers.items():
            left_top_x_square = value[0] - square_size // 2
            left_top_y_square = value[1] - square_size // 2
            square = whole_screen.crop((left_top_x_square + square_boundary_pixels,
                                        left_top_y_square + square_boundary_pixels,
                                        left_top_x_square + square_size - square_boundary_pixels,
                                        left_top_y_square + square_size - square_boundary_pixels))
            are_there = HelpersToAnalyzeChessboard.are_there_colours_in_a_PIL_image(square, highlighted_colours)
            if are_there["is_there"]:
                highlighted_squares.append(key)

        return highlighted_squares

    def get_highlighted_squares_from_picture_kurnik(whole_screen, square_centers, square_size, highlighted_colours):
        highlighted_squares = []

        # Defining how big part of a square will be cut out to allow for some
        #   inacurracies in square identification (so that the highlighted
        #   colours are really found only on two squares)
        square_boundary = 0
        square_boundary_pixels = square_size * square_boundary

        # Looping through all squares, and testing if they contain highlighted
        #   colour
        for key, value in square_centers.items():
            left_top_x_square = value[0] - square_size // 2
            left_top_y_square = value[1] - square_size // 2
            square = whole_screen.crop((left_top_x_square + square_boundary_pixels,
                                        left_top_y_square + square_boundary_pixels,
                                        left_top_x_square + square_size - square_boundary_pixels,
                                        left_top_y_square + square_size - square_boundary_pixels))

            # Creating four sub-squares, to test if the colour is present in
            #   at least three of them - which signs success
            length = square.size[0]
            step = length // 2
            sub_squares = [
                (0, 0, step , step),
                (step, 0, step * 2 , step),
                (0, step, step , step * 2),
                (step, step, step * 2 , step * 2)
            ]

            found = 0
            for sub_square in sub_squares:
                smaller_square = square.crop(sub_square)
                are_there = HelpersToAnalyzeChessboard.are_there_colours_in_a_PIL_image(
                    smaller_square, highlighted_colours)
                if are_there["is_there"]:
                    found += 1

            if found > 2:
                highlighted_squares.append(key)

        return highlighted_squares

    def drag_mouse_from_square_to_square(from_square, to_square):
        initial_position = pyautogui.position()

        try:
            from_center = square_centers[from_square]
        except KeyError:
            print("Coordination '{}' does not exist!".format(from_square))
            return

        try:
            to_center = square_centers[to_square]
        except KeyError:
            print("Coordination '{}' does not exist!".format(to_square))
            return

        pyautogui.click(*from_center)
        pyautogui.click(*to_center)

        pyautogui.moveTo(*initial_position)
        pyautogui.click(*initial_position)

# Initializing the coordinates and below having the possibility of choosing
#   already known websites, where we know the coordinates of the chessboard
left_top = None
right_bottom = None

# https://lichess.org/editor
# left_top = (479, 291)
# right_bottom = (1026, 837)

# https://www.chess.com/cs/analysis
# left_top = (351, 152)
# right_bottom = (1206, 1007)

# https://www.chess.com/cs/play/computer
# left_top = (460, 170)
# right_bottom = (1277, 982)

# https://www.playok.com/cs/sachy/
left_top = (425, 208)
right_bottom = (1108, 889)


# Seeing if we have not already assigned the board, in that case find the coords
if left_top is None:
    print("Please rightlick the most upperleft corner of the chessboard")
    with mouse.Listener(
            on_click=HelpersToAssignChessboard.on_click) as listener:
        listener.join()


# Getting the chessboard dimensions
board_size = right_bottom[0] - left_top[0]
square_size = board_size // 8
square_centers = HelpersToAssignChessboard.create_dict_of_square_centers(left_top, right_bottom, our_colour)
print("board_size", board_size)
print("square_size", square_size)
print("square_centers", square_centers)

# Determining which colours are a sign of a piece movement
# This info is specific to chess.com
white_field_highlight_colour = (246, 246, 130)
black_field_highlight_colour = (186, 202, 68)
# highlighted_colours = [white_field_highlight_colour, black_field_highlight_colour]
highlighted_colours = [(47, 66, 45), (17, 53, 20)]

# Defining loop variables and parameters
previously_highlighted_squares = []
our_colour_chess = chess.WHITE if our_colour == "white" else chess.BLACK
sleep_interval = 0.2
first_move_played_as_white = False

# Serving as a convenient starter
input("After you press Enter, the recording will begin!")

# Start an infinite watching loop
print("Starting to observe the board")
while True:
    time.sleep(sleep_interval)
    # Making sure we play the first move when we are white, and we do not response as black
    if our_colour == "white" and board.fullmove_number == 1 and not first_move_played_as_white:
        # Figuring out the current best move as a response
        result = engine.play(board, limit)

        # Parsing two squares that define the current move
        # Promoting a pawn has a structure of c2c1q
        move_string = str(result.move)
        from_square = move_string[0:2]
        to_square = move_string[2:4]

        # Playing the move on the screen chessboard
        HelpersToAnalyzeChessboard.drag_mouse_from_square_to_square(from_square, to_square)

        # Playing the move on an internal board
        board.push(result.move)

        print("I AM PLAYING {}!!".format(result.move))
        first_move_played_as_white = True

    # Making a screenshot of the whole screen
    whole_screen = pyautogui.screenshot()

    # Getting a list of (in most cases 2) squares that are highlighted
    #   as a sign of previous move
    # highlighted_squares = HelpersToAnalyzeChessboard.get_highlighted_squares_from_picture(
    #     whole_screen, square_centers, square_size, highlighted_colours)
    highlighted_squares = HelpersToAnalyzeChessboard.get_highlighted_squares_from_picture_kurnik(
        whole_screen, square_centers, square_size, highlighted_colours)

    # When there is a new valid highlighted situation, determine what move
    #   was played and also come up with a move
    if len(highlighted_squares) == 2 and highlighted_squares != previously_highlighted_squares:
        print("we should make a move!!!")
        move_that_was_done = None

        possible_moves_from_highlight = [highlighted_squares[0] + highlighted_squares[1], highlighted_squares[1] + highlighted_squares[0]]

        # Looping through all (2) possibilities of movement between the two
        #   highlighted squares, and determining, which one of them is a valid move
        for move in possible_moves_from_highlight:
            if chess.Move.from_uci(move) in board.legal_moves:
                print("WE HAVE FOUND A MOVE!!! - {}".format(move))
                move_that_was_done = move
                break

        if move_that_was_done:
            if board.turn == our_colour_chess:
                print("not our turn")
                continue
            # Playing the move on an internal board
            board.push(chess.Move.from_uci(move_that_was_done))
            print("move was done: {}".format(chess.Move.from_uci(move_that_was_done)))

            # Figuring out the current best move as a response
            result = engine.play(board, limit)

            # Parsing two squares that define the current move
            # Promoting a pawn has a structure of c2c1q
            move_string = str(result.move)
            from_square = move_string[0:2]
            to_square = move_string[2:4]

            # Playing the move on the screen chessboard
            HelpersToAnalyzeChessboard.drag_mouse_from_square_to_square(from_square, to_square)
            # If there is a promotion, presume we will have a queen, so click
            #   the to_square once again
            # TODO: add a picture of a promotion queen to the game
            if len(move_string) > 4:
                pyautogui.click(square_centers[to_square])

            # Playing the move on an internal board
            board.push(result.move)

            print("I AM PLAYING {}!!".format(result.move))

        previously_highlighted_squares = highlighted_squares

    # When the game is over, terminate the loop
    if board.is_game_over():
        print("CONGRATULATIONS!!")
        break
