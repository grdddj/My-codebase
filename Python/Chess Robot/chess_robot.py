"""
This script is playing chess without any human intervention (almost).
Just define the coordination of the chessboard and some identificator
    of the oponent moves, and it is ready to beat even the strongest
    grandmasters!
Was developed mostly on chess.com, lichess.org and playok.com,
    but can be relatively easily upgraded to handle almost any chessboard.

Possible improvements:
- listen for certain keys when being turned on and off, so we do not have
    to leave the mouse from playing window (which is visible to oponent)
"""

import pyautogui
from pynput import keyboard
import time

# Documentation here: https://python-chess.readthedocs.io/en/latest/
import chess
import chess.engine

from helpers import HelpersToAssignChessboard, HelpersToAnalyzeChessboard
from config import Config


class NoNewMoveFoundOnTheChessboard(Exception):
    '''
    Custom exception that will be thrown when we find out there
        is no new move, to quickly skip all other checks
    '''

    def __init__(self, description: str = ""):
        self.description = description

    def __str__(self):
        return f"No new move found. Description: {self.description}"


class TheGameHasFinished(Exception):
    '''
    Custom exception that will be thrown when we find out
        the game has finished, to start a new game
    '''

    def __init__(self, result: str = ""):
        self.result = result

    def __str__(self):
        return f"The game has finished. Result: {self.result}"


class ChessRobot:
    def __init__(self, observer_only_mode: bool = False):
        self.observer_only_mode = observer_only_mode

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
        self.currently_highlighted_squares = []
        self.our_last_move_from_and_to = []

        self.current_best_move = None

    def start_the_game(self) -> None:
        self.get_our_colour_from_user()
        self.get_chessboard_boundaries_if_not_set()
        self.get_chessboard_details()
        input("After you press Enter, the play will begin!")
        self.start_observing_the_chessboard()

    def get_our_colour_from_user(self) -> None:
        print("Be sure to play on your main screen. Please move the console to a second screen.")
        colour_input = input("Choose the colour (WHITE/(b)lack): ")
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
        if not self.observer_only_mode:
            self.play_first_move_as_white_if_necessary()
        print("Starting to observe the board")
        while True:
            time.sleep(Config.sleep_interval_between_screenshots)
            try:
                self.watch_on_the_chessboard()
            except NoNewMoveFoundOnTheChessboard:
                continue
            except TheGameHasFinished:
                break

    def watch_on_the_chessboard(self) -> None:
        self.get_currently_highlighted_squares()
        self.check_if_some_new_move_was_done()

        if not self.observer_only_mode:
            self.check_if_last_move_was_not_done_by_us()

        self.recognize_move_done_on_the_board()
        self.play_the_move_from_the_board_on_internal_board()

        if self.board.is_game_over():
            print("SEEMS WE HAVE LOST. MAYBE NEXT TIME!!")
            raise TheGameHasFinished("You have lost!")

        self.suggest_the_best_move()
        self.evaluate_the_position()

        if not self.observer_only_mode:
            self.perform_the_best_move_on_the_screen_and_also_internally()

            if self.board.is_game_over():
                print("YOU HAVE WON, CONGRATULATIONS!!")
                raise TheGameHasFinished("You have won!")

    def play_first_move_as_white_if_necessary(self) -> None:
        # Making sure we play the first move when we are white
        we_should_start_as_white = (
            self.our_colour == "white"
            and
            self.board.fullmove_number == 1
        )
        if we_should_start_as_white:
            print("Kicking the game by playing first")
            self.suggest_the_best_move()
            self.perform_the_best_move_on_the_screen_and_also_internally()

    def get_currently_highlighted_squares(self) -> None:
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

        self.currently_highlighted_squares = highlighted_squares

    def check_if_some_new_move_was_done(self) -> None:
        # When there is a new valid highlighted situation, determine what move
        #   was played and also come up with a move
        some_move_was_done = (
            len(self.currently_highlighted_squares) == 2
            and
            self.currently_highlighted_squares != self.previously_highlighted_squares
        )

        self.previously_highlighted_squares = self.currently_highlighted_squares

        if not some_move_was_done:
            raise NoNewMoveFoundOnTheChessboard("No new highlight")

    def check_if_last_move_was_not_done_by_us(self) -> None:
        highlighted_move_is_ours = (
            self.our_last_move_from_and_to == self.currently_highlighted_squares
            or
            self.our_last_move_from_and_to == list(reversed(self.currently_highlighted_squares))
        )
        if highlighted_move_is_ours:
            print("Last move was ours, it is opponents's turn")
            raise NoNewMoveFoundOnTheChessboard("Last move was ours")

    def recognize_move_done_on_the_board(self) -> None:
        print("We have identified a new move on the board!!!")
        self.move_done_on_the_board = None

        possible_moves_from_highlight = [
            self.currently_highlighted_squares[0] + self.currently_highlighted_squares[1],
            self.currently_highlighted_squares[1] + self.currently_highlighted_squares[0]
        ]

        # Looping through all (2) possibilities of movement between the two
        #   highlighted squares, and determining, which one of them is a valid move
        for move in possible_moves_from_highlight:
            if chess.Move.from_uci(move) in self.board.legal_moves:
                self.move_done_on_the_board = move
                break

        if not self.move_done_on_the_board:
            print("No move was done - please investigate, why")
            print("possible_moves_from_highlight", possible_moves_from_highlight)
            print("our_last_move_from_and_to", self.our_last_move_from_and_to)
            print("highlighted_squares", self.currently_highlighted_squares)
            raise NoNewMoveFoundOnTheChessboard("Something inconsistent happened")

    def play_the_move_from_the_board_on_internal_board(self) -> None:
        move = chess.Move.from_uci(self.move_done_on_the_board)
        self.play_move_on_our_internal_board(move)

    def play_move_on_our_internal_board(self, move) -> None:
        self.board.push(move)
        move_human = self._translate_move_into_human_readable(move)
        print(f"Move done in internal board: {move_human}")

    def perform_the_best_move_on_the_screen_and_also_internally(self) -> None:
        if Config.wait_for_keyboard_trigger_to_play:
            print("Waiting for trigger: ", Config.keyboard_trigger)
            with keyboard.Listener(on_release=press_trigger) as listener:
                listener.join()

        self.do_the_move_on_screen_chessboard(self.current_best_move)
        self.play_move_on_our_internal_board(self.current_best_move)

    def suggest_the_best_move(self) -> None:
        self.current_best_move = self.engine.play(self.board, self.time_limit_to_analyze).move
        best_move_human = self._translate_move_into_human_readable(self.current_best_move)
        print(f"I would play ***** {best_move_human} *****")

    @staticmethod
    def _translate_move_into_human_readable(move) -> str:
        move_string = str(move)
        from_square = move_string[0:2]
        to_square = move_string[2:4]

        return f"{from_square} - {to_square}"

    def do_the_move_on_screen_chessboard(self, move) -> None:
        move_string = str(move)
        from_square = move_string[0:2]
        to_square = move_string[2:4]

        print(f"I AM PLAYING {from_square} - {to_square}")

        # Playing the move on the screen chessboard
        HelpersToAnalyzeChessboard.drag_mouse_from_square_to_square(
            self.square_centers, from_square, to_square)

        self.our_last_move_from_and_to = [from_square, to_square]

        # If there is a promotion, presume we will have a queen, so click
        #   the to_square once again
        if len(move_string) > 4:
            pyautogui.click(self.square_centers[to_square])

    def evaluate_the_position(self) -> None:
        info = self.engine.analyse(self.board, chess.engine.Limit(depth=15))
        if self.our_colour == "white":
            score_from_our_point = info["score"].white()
        else:
            score_from_our_point = info["score"].black()

        try:
            pawn_points = int(str(score_from_our_point)) / 100
            print("Score:", pawn_points)
        except ValueError:
            print("Checkmate soon", score_from_our_point)


def press_trigger(key):
    if key == Config.keyboard_trigger:
        print("Pressing trigger!")
        return False


if __name__ == "__main__":
    while True:
        try:
            robot = ChessRobot()
            robot.start_the_game()
        except KeyboardInterrupt:
            print("Thank you for the games!")
            break
