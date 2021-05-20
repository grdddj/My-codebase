"""
This script is playing chess without any human intervention (almost).
Just define the coordination of the chessboard and some identificator
    of the oponent moves, and it is ready to beat even the strongest
    grandmasters!
Is tuned for websites chess.com and playok.com, but can be relatively easily
    upgraded to handle almost any chessboard.

Possible improvements:
- handling of promotion via image recognition

- wait for some variable time before making a move, not to look suspicious
- listen for certain keys when being turned on and off, so we do not have
    to leave the mouse from playing window (which is visible to oponent)
- having a command key that would issue the move (press it, move) - and
    wait for this before moving, to create authentic play (fast and slow)
"""

import pyautogui
import time

# Documentation here: https://python-chess.readthedocs.io/en/latest/
import chess
import chess.engine

from helpers import HelpersToAssignChessboard, HelpersToAnalyzeChessboard
from config import Config


class ChessRobot:
    def __init__(self):
        self.CHESSBOARD_ASSIGNER = HelpersToAssignChessboard()
        self.board = chess.Board()
        self.engine = chess.engine.SimpleEngine.popen_uci(Config.engine_location)
        self.time_limit_to_analyze = chess.engine.Limit(time=Config.time_limit_to_think)

        self.our_colour = None
        self.left_top_pixel_coords = None
        self.right_bottom_pixel_coords = None
        self.board_size = None
        self.square_size = None
        self.square_centers = None

        self.colours_of_highlighted_moves = [
            Config.white_field_highlight_colour,
            Config.black_field_highlight_colour
        ]

        self.previously_highlighted_squares = []
        self.our_last_move_from_and_to = []

    def start_the_game(self) -> None:
        self.get_our_colour_from_user()
        self.get_chessboard_boundaries_if_not_set()
        self.get_chessboard_details()
        self.start_observing_the_chessboard()

    def get_our_colour_from_user(self) -> None:
        print("Be sure to play on your main screen. Please move the console to a second screen.")
        colour_input = input("Choose the colour: WHITE/(b)lack")
        if colour_input and colour_input[0].lower() == "b":
            self.our_colour = "black"
        else:
            self.our_colour = "white"
        print("You chose {} pieces, good luck in the game!".format(self.our_colour))

    def get_chessboard_boundaries_if_not_set(self) -> None:
        # Initializing the coordinates and below having the possibility of choosing
        #   already known websites, where we know the coordinates of the chessboard
        self.left_top = Config.left_top
        self.right_bottom = Config.right_bottom

        # Seeing if we have not already assigned the board, in that case find the coords
        if self.left_top is None or self.right_bottom is None:
            self.left_top, self.right_bottom = self.CHESSBOARD_ASSIGNER.get_left_top_and_right_bottom()

    def get_chessboard_details(self) -> None:
        self.board_size = self.right_bottom[0] - self.left_top[0]
        self.square_size = self.board_size // 8
        self.square_centers = self.CHESSBOARD_ASSIGNER.create_dict_of_square_centers(
            self.left_top, self.right_bottom, self.our_colour)

    def start_observing_the_chessboard(self) -> None:
        # Serving as a convenient starter
        input("After you press Enter, the play will begin!")

        # Making sure we play the first move when we are white
        we_should_start_as_white = (
            self.our_colour == "white"
            and
            self.board.fullmove_number == 1
        )
        if we_should_start_as_white:
            print("Kicking the game by playing first")
            self.do_a_move_by_ourselves()

        # Start an infinite watching loop
        print("Starting to observe the board")
        while True:
            time.sleep(Config.sleep_interval_between_screenshots)

            # Making a screenshot of the whole screen
            whole_screen = pyautogui.screenshot()

            # Getting a list of (in most cases 2) squares that are highlighted
            #   as a sign of previous move
            if Config.website == "kurnik":
                func = HelpersToAnalyzeChessboard.get_highlighted_squares_from_picture_kurnik
            else:
                func = HelpersToAnalyzeChessboard.get_highlighted_squares_from_picture
            highlighted_squares = func(
                whole_screen, self.square_centers, self.square_size, self.colours_of_highlighted_moves)

            # When there is a new valid highlighted situation, determine what move
            #   was played and also come up with a move
            some_move_was_done = (
                len(highlighted_squares) == 2
                and
                highlighted_squares != self.previously_highlighted_squares
            )
            if not some_move_was_done:
                continue

            self.previously_highlighted_squares = highlighted_squares

            # It is opponent's turn
            highlighted_move_is_ours = (
                self.our_last_move_from_and_to == highlighted_squares
                or
                self.our_last_move_from_and_to == list(reversed(highlighted_squares))
            )
            if highlighted_move_is_ours:
                print("Last move was ours, it is opponents's turn")
                continue

            print("We have identified a new move by opponent!!!")
            move_done_by_opponent = None

            possible_moves_from_highlight = [
                highlighted_squares[0] + highlighted_squares[1],
                highlighted_squares[1] + highlighted_squares[0]
            ]

            # Looping through all (2) possibilities of movement between the two
            #   highlighted squares, and determining, which one of them is a valid move
            for move in possible_moves_from_highlight:
                if chess.Move.from_uci(move) in self.board.legal_moves:
                    move_done_by_opponent = move
                    break

            if not move_done_by_opponent:
                print("No move was done - please investigate, why")
                print("possible_moves_from_highlight", possible_moves_from_highlight)
                print("our_last_move_from_and_to", self.our_last_move_from_and_to)
                print("highlighted_squares", highlighted_squares)
                continue

            # Playing the opponent's move on an internal board
            self.board.push(chess.Move.from_uci(move_done_by_opponent))
            print("Move was done by opponent: {}".format(chess.Move.from_uci(move_done_by_opponent)))

            if self.board.is_game_over():
                print("SEEMS WE HAVE LOST. MAYBE NEXT TIME!!")
                break

            self.do_a_move_by_ourselves()

            if self.board.is_game_over():
                print("YOU HAVE WON, CONGRATULATIONS!!")
                break

    def do_a_move_by_ourselves(self) -> None:
        # Figuring out the current best move as a response
        result = self.engine.play(self.board, self.time_limit_to_analyze)

        # Parsing two squares that define the current move
        # Promoting a pawn has a structure of c2c1q
        move_string = str(result.move)
        from_square = move_string[0:2]
        to_square = move_string[2:4]
        self.our_last_move_from_and_to = [from_square, to_square]

        # Playing the move on the screen chessboard
        HelpersToAnalyzeChessboard.drag_mouse_from_square_to_square(
            self.square_centers, from_square, to_square)

        # If there is a promotion, presume we will have a queen, so click
        #   the to_square once again
        # TODO: add a picture of a promotion queen to the game
        if len(move_string) > 4:
            pyautogui.click(self.square_centers[to_square])

        # Playing the move on an internal board
        self.board.push(result.move)

        print("I AM PLAYING {}!!".format(result.move))


if __name__ == "__main__":
    while True:
        try:
            robot = ChessRobot()
            robot.start_the_game()
        except KeyboardInterrupt:
            print("Thank you for the games!")
            break
