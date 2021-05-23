"""
This script is playing chess without any human intervention (almost).
Just define the coordination of the chessboard and some identificator
    of the oponent moves, and it is ready to beat even the strongest
    grandmasters!
Was developed mostly on chess.com, lichess.org and playok.com,
    but can be relatively easily upgraded to handle almost any chessboard.

Basic high-level flow:
- Gets the colour from user input
    (self.our_chess_colour)
- Gets the coordinates of the chessboard on the screen from config or from user input
    (self.chessboard_left_top_pixel, self.chessboard_right_bottom_pixel)
- Maps all the 64 squares with the coordination of its center
    (self.square_centers_dict)
- Needs to know the colours that will mean highlighted square
    (self.colours_of_highlighted_moves)
- Sets up the internal chess board connected with chess engine
    (self.board, self.engine)
- Observes the screen chessboard in infinite loop:
    (self.look_at_the_chessboard_and_react_on_new_moves)
    - Finds out if two squares are highlighted
    - Finds out if these squares form a valid opponent's move
    - Plays that move on the internal chess board
    - Suggests the best continuation for our side
    - Plays that best continuation on the screen and on internal board
    - Evaluates the position

Useful to know (features):
- Lot of options in the config file
- Any time the script can be killed by Ctrl+C in the console
- After the game finishes, it will offer to start again
- When we find out we are already winning, we do not spend so much time
    thinking/evaluating to play faster

Possible improvements:
- listen for certain keys when being turned on and off, so we do not have
    to leave the mouse from playing window (which is visible to oponent)
- parse the time from the screen and reflect it in the time of analysis
    (play faster when having less time)
"""

import pyautogui  # type: ignore
from pynput import keyboard  # type: ignore
import time

from typing import List, Union

# Documentation here: https://python-chess.readthedocs.io/en/latest/
import chess
import chess.engine

from helpers import HelpersToAssignChessboard
from helpers import HelpersToAnalyzeChessboard

from config import Config

# Making all pyautogui actions faster, default is 0.1 seconds
pyautogui.PAUSE = 0.01


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
        # Do not play the moves on the screen, just suggest them
        self.observer_only_mode = observer_only_mode

        self.CHESSBOARD_ASSIGNER = HelpersToAssignChessboard()
        self.CHESSBOARD: HelpersToAnalyzeChessboard
        self.board = chess.Board()
        self.engine = chess.engine.SimpleEngine.popen_uci(Config.engine_location)

        self.our_chess_colour: chess.Color
        self.our_colour_string: str
        self.chessboard_left_top_pixel: tuple
        self.chessboard_right_bottom_pixel: tuple

        self.colours_of_highlighted_moves = [
            Config.white_field_highlight_colour,
            Config.black_field_highlight_colour
        ]

        self.previously_highlighted_squares: List[str] = []
        self.currently_highlighted_squares: List[str] = []
        self.our_last_move_from_and_to: List[str] = []
        self.move_done_on_the_board = ""

        self.current_analysis_result: chess.engine.InfoDict
        self.current_best_move: chess.Move
        self.last_position_evaluation: Union[float, chess.engine.Score] = 0.0
        self.last_position_situation = "normal"  # "losing", "normal", "winning", "mate soon"

    def start_the_game(self) -> None:
        self.get_our_colour_from_user()
        self.get_chessboard_boundaries_if_not_defined()
        self.get_chessboard_details_and_create_chessboard_object()
        input("After you press Enter, the play will begin!")
        self.start_observing_the_chessboard()

    def get_our_colour_from_user(self) -> None:
        print("Be sure to play on your main screen. Please move the console to a second screen.")
        colour_input = input("Choose the colour (WHITE/(b)lack): ")
        if colour_input and colour_input[0].lower() == "b":
            self.our_chess_colour = chess.BLACK
        else:
            self.our_chess_colour = chess.WHITE
        self.our_colour_string = "white" if self.our_chess_colour == chess.WHITE else "black"
        print(f"You chose {self.our_colour_string} pieces, good luck in the game!")

    def get_chessboard_boundaries_if_not_defined(self) -> None:
        # Boundaries may, or may not be defined in config
        try:
            self.chessboard_left_top_pixel = Config.chessboard_left_top_pixel
            self.chessboard_right_bottom_pixel = Config.chessboard_right_bottom_pixel
        except AttributeError:
            boundaries = self.CHESSBOARD_ASSIGNER.get_left_top_and_right_bottom_chessboard_pixels()
            self.chessboard_left_top_pixel = boundaries[0]
            self.chessboard_right_bottom_pixel = boundaries[1]

    def get_chessboard_details_and_create_chessboard_object(self) -> None:
        chessboard_size = self.chessboard_right_bottom_pixel[0] - self.chessboard_left_top_pixel[0]
        square_size = chessboard_size // 8
        square_centers_dict = self.CHESSBOARD_ASSIGNER.create_dict_of_square_centers(
            chessboard_left_top_pixel=self.chessboard_left_top_pixel,
            chessboard_right_bottom_pixel=self.chessboard_right_bottom_pixel,
            our_colour=self.our_colour_string
        )
        self.CHESSBOARD = HelpersToAnalyzeChessboard(
            square_centers_dict=square_centers_dict,
            square_size=square_size,
            highlighted_colours=self.colours_of_highlighted_moves,
        )

    def start_observing_the_chessboard(self) -> None:
        if not self.observer_only_mode:
            self.play_first_move_as_white_if_necessary()

        print("Starting to observe the board")
        while True:
            time.sleep(Config.sleep_interval_between_screenshots)
            try:
                self.look_at_the_chessboard_and_react_on_new_moves()
            except NoNewMoveFoundOnTheChessboard:
                continue
            except TheGameHasFinished:
                break

    def play_first_move_as_white_if_necessary(self) -> None:
        we_should_start_as_white = (
            self.our_chess_colour == chess.WHITE
            and
            self.board.fullmove_number == 1
        )
        if we_should_start_as_white:
            print("Kicking the game by playing first")
            self.analyze_position_and_suggest_the_best_move()
            self.perform_the_best_move_on_the_screen_and_internally()

    def look_at_the_chessboard_and_react_on_new_moves(self) -> None:
        self.get_currently_highlighted_squares()
        self.check_if_some_new_move_was_done()

        if not self.observer_only_mode:
            self.check_if_last_move_was_not_done_by_us()

        self.recognize_move_done_on_the_board()
        self.play_the_move_from_the_board_on_internal_board()

        self.check_if_the_game_did_not_finish()

        self.analyze_position_and_suggest_the_best_move()

        if not self.observer_only_mode:
            self.perform_the_best_move_on_the_screen_and_internally()

        self.check_if_the_game_did_not_finish()

    def get_currently_highlighted_squares(self) -> None:
        # Making a screenshot of the whole screen
        whole_screen = pyautogui.screenshot()

        # Quick check if the previously highlighted squares are still
        #   highlighted - having to check only 2 squares instead of 64
        if self.previously_highlighted_squares:
            highlight_did_not_change = self.CHESSBOARD.check_if_squares_are_highlighted(
                whole_screen=whole_screen,
                squares_to_check=self.previously_highlighted_squares,
            )
            if highlight_did_not_change:
                raise NoNewMoveFoundOnTheChessboard("Same highlight as before")

        # Getting a list of (in most cases 2) squares that are highlighted
        #   as a sign of previous move (is website dependant)
        if Config.website == "kurnik":
            self.currently_highlighted_squares = self.CHESSBOARD.get_highlighted_squares_from_picture_kurnik(
                whole_screen=whole_screen
            )
        else:
            self.currently_highlighted_squares = self.CHESSBOARD.get_highlighted_squares_from_picture(
                whole_screen=whole_screen
            )

    def check_if_some_new_move_was_done(self) -> None:
        # When there is a new valid highlighted situation, determine what move
        #   was played and also come up with a move
        some_move_was_done = (
            len(self.currently_highlighted_squares) == 2
            and
            self.currently_highlighted_squares != self.previously_highlighted_squares
        )

        if not some_move_was_done:
            raise NoNewMoveFoundOnTheChessboard("No new highlight")
        else:
            self.previously_highlighted_squares = self.currently_highlighted_squares

    def check_if_last_move_was_not_done_by_us(self) -> None:
        highlighted_move_is_ours = (
            self.our_last_move_from_and_to[0] in self.currently_highlighted_squares
            and
            self.our_last_move_from_and_to[1] in self.currently_highlighted_squares
        )
        if highlighted_move_is_ours:
            print("Last move was ours, it is opponents's turn")
            raise NoNewMoveFoundOnTheChessboard("Last move was ours")

    def recognize_move_done_on_the_board(self) -> None:
        self.move_done_on_the_board = ""

        possible_moves_from_highlight = [
            self.currently_highlighted_squares[0] + self.currently_highlighted_squares[1],
            self.currently_highlighted_squares[1] + self.currently_highlighted_squares[0]
        ]

        # Looping through all (2) possibilities of movement between the two
        #   highlighted squares, and determining, which one of them is a valid move
        for candidate_move in possible_moves_from_highlight:
            if chess.Move.from_uci(candidate_move) in self.board.legal_moves:
                print(f"We have identified a new move on the board - {candidate_move}")
                self.move_done_on_the_board = candidate_move
                break

        # In ideal condition this should never happen, but in practice
        #   can, when these is some inconsistency (it did not catch some move)
        if not self.move_done_on_the_board:
            print("No move was done - please investigate, why")
            print("MOST PROBABLY THE MOVE WAS NOT DONE ON THE SCREEN BY PYAUTOGUI")
            print("possible_moves_from_highlight", possible_moves_from_highlight)
            print("our_last_move_from_and_to", self.our_last_move_from_and_to)
            print("highlighted_squares", self.currently_highlighted_squares)
            raise NoNewMoveFoundOnTheChessboard("Something inconsistent happened")

    def perform_the_best_move_on_the_screen_and_internally(self) -> None:
        if Config.wait_for_keyboard_trigger_to_play:
            print("Waiting for trigger to play move: ", Config.keyboard_trigger)
            with keyboard.Listener(on_release=press_trigger_to_play_move) as listener:
                listener.join()

        # TODO: should somehow check if the move was really done on the screen,
        #   as rarely it can fail, if the mouse is being used by user
        self.do_the_move_on_screen_chessboard(self.current_best_move)
        self.play_move_on_our_internal_board(self.current_best_move)

    def do_the_move_on_screen_chessboard(self, move: chess.Move) -> None:
        from_square, to_square = self.get_to_and_from_square_from_the_move(move)

        human_readable = self._translate_move_into_human_readable(move)
        print(f"I AM PLAYING {human_readable}")

        # Playing the move on the screen chessboard
        # TODO: could have a check that the move was really performed
        #   on the screen - and if not - try to do it again
        self.CHESSBOARD.drag_mouse_from_square_to_square(
            from_square=from_square,
            to_square=to_square
        )

        self.our_last_move_from_and_to = [from_square, to_square]

        # If there is a promotion, presume we will have a queen, so click
        #   the to_square once again
        if len(str(move)) > 4:
            self.CHESSBOARD.click_on_square(to_square)

    def play_the_move_from_the_board_on_internal_board(self) -> None:
        move = chess.Move.from_uci(self.move_done_on_the_board)
        self.play_move_on_our_internal_board(move)

    def play_move_on_our_internal_board(self, move: chess.Move) -> None:
        # NOTE: we must first retrieve the move and only then push it one
        #   the board, otherwise the SAN representation would fail
        #   (it only takes valid moves in current situation)
        move_human = self._translate_move_into_human_readable(move)
        print(f"Move done on our internal board: {move_human}")
        self.board.push(move)

    def analyze_position_and_suggest_the_best_move(self) -> None:
        self.get_current_analysis_result()

        self.get_position_evaluation_from_analysis_result()
        self.reflect_evaluation_into_situation()

        self.get_the_current_best_move_from_analysis_result()

    def get_current_analysis_result(self) -> None:
        time_to_think = self.get_time_to_think_according_to_the_last_position()
        self.current_analysis_result = self.engine.analyse(
            board=self.board,
            limit=chess.engine.Limit(time=time_to_think),
        )

    def get_time_to_think_according_to_the_last_position(self) -> float:
        if self.last_position_situation in ["winning", "mate soon"]:
            return Config.time_limit_to_think_when_already_winning
        elif self.last_position_situation == "losing":
            return Config.time_limit_to_think_when_losing
        else:
            return Config.time_limit_to_think_normal

    def get_position_evaluation_from_analysis_result(self) -> None:
        score_from_our_side = self.current_analysis_result["score"].pov(self.our_chess_colour)
        if self.current_analysis_result["score"].is_mate():
            self.last_position_evaluation = score_from_our_side
            print("Checkmate soon", score_from_our_side)
        else:
            pawn_points = int(str(score_from_our_side)) / 100
            self.last_position_evaluation = pawn_points
            print("Score:", pawn_points)

    def reflect_evaluation_into_situation(self) -> None:
        self.last_position_situation = self.get_situation_from_the_evaluation()

    def get_situation_from_the_evaluation(self) -> str:
        # self.last_position_evaluation will either be float or Mate object
        #   (throws TypeError in that case)
        try:
            if self.last_position_evaluation > Config.pawn_threshold_when_already_winning:
                return "winning"
            elif self.last_position_evaluation < Config.pawn_threshold_when_losing:
                return "losing"
            else:
                return "normal"
        except TypeError:
            return "mate soon"

    def get_the_current_best_move_from_analysis_result(self) -> None:
        self.current_best_move = self.current_analysis_result["pv"][0]
        best_move_human = self._translate_move_into_human_readable(self.current_best_move)
        print(f"I would play ***** {best_move_human} *****")

    def _translate_move_into_human_readable(self, move: chess.Move) -> str:
        from_square, to_square = self.get_to_and_from_square_from_the_move(move)
        classic_notation = self.board.san(move) if move else "None"
        return f"{from_square} - {to_square} ({classic_notation})"

    @staticmethod
    def get_to_and_from_square_from_the_move(move: chess.Move) -> tuple:
        move_string = str(move)
        from_square = move_string[0:2]
        to_square = move_string[2:4]

        return from_square, to_square

    def check_if_the_game_did_not_finish(self) -> None:
        if self.board.is_game_over():
            self.evaluate_winner_and_finish_the_game()

    def evaluate_winner_and_finish_the_game(self) -> None:
        outcome = self.board.outcome()
        if not outcome:
            return

        if outcome.winner is True:
            print("YOU HAVE WON, CONGRATULATIONS!!")
            raise TheGameHasFinished("You have won!")
        elif outcome.winner is False:
            print("YOU HAVE LOST, MAYBE NEXT TIME!!")
            raise TheGameHasFinished("You have lost!")
        else:
            print("DRAW - WHAT A GAME!!")
            raise TheGameHasFinished("Draw!")


def press_trigger_to_play_move(key):
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
