"""
This script is playing chess without any human intervention (almost).
Just define the coordination of the chessboard and some identificator
    of the opponent moves, and it is ready to beat even the strongest
    grandmasters!
Was developed mostly on chess.com, lichess.org and playok.com,
    but can be relatively easily upgraded to handle almost any chessboard.

Basic high-level flow:
- Observes the screen chessboard in infinite loop:
    (self._look_at_the_chessboard_and_react_on_new_moves)
    - Finds out if two squares are highlighted
    - Finds out if these squares form a valid opponent's move
    - Plays that move on the internal chess board
    - Evaluates the position and suggests the best continuation for our side
    - Plays that best continuation on the screen and on internal board

Useful to know (features):
- Lot of options in the config file
- Any time the script can be killed by Ctrl+C in the console
- After the game finishes, it will offer to start again
- When we find out we are already winning, we do not spend so much time
    thinking/evaluating to play faster

Performance:
- when waiting for a new move, with `self.config.should_sleep = False`,
    it analyzes the board every 50 ms (90 % of the time is 
    taken by screenshotting the screen)
- playing a move on the screen takes also around 50 ms
- therefore, with `time_limit_to_think_normal = 0.1`, each move takes
    around 200 ms
- it plays very well even with `time_limit_to_think_normal = 0.01`, which
    speeds up the play quite a lot (can play up to 10 moves per second)

Possible improvements:
- parse the time from the screen and reflect it in the time of analysis
    (play faster when having less time)
- protection against "premove" - when the opponent fires a move
    immediately after we play - and program cannot recognize two moves
    happened at once
- show the suggested moves on the screen in observer mode

DISCLAIMER:
- this project was done only for educational purposes, author has no
    interest in actually using it against real human players to cheat
- author bears no responsibility for the script being used for
    any illicit purposes, other than learning programming in python
"""

from __future__ import annotations

import time
from enum import Enum
from typing import TYPE_CHECKING

from api import ChessResult, Square, Move
from helpers import get_screenshot, wait_for_keyboard_trigger

if TYPE_CHECKING:
    from api import (
        ChessboardMonitoringInterface,
        ChessboardPlayingInterface,
        ChessLibraryInterface,
        ConfigInterface,
    )


class ChessPositionEvaluation(Enum):
    Normal = 1
    Winning = 2
    Losing = 3
    MateSoon = 4


class NoNewMoveFoundOnTheChessboard(Exception):
    """
    Custom exception that will be thrown when we find out there
        is no new move, to quickly skip all other checks
    """

    def __init__(self, description: str = "") -> None:
        self.description = description

    def __str__(self) -> str:
        return f"No new move found. Description: {self.description}"


class TheGameHasFinished(Exception):
    """
    Custom exception that will be thrown when we find out
        the game has finished, to start a new game
    """

    def __init__(self, result: str = "") -> None:
        self.result = result

    def __str__(self) -> str:
        return f"The game has finished. Result: {self.result}"


class ChessRobot:
    def __init__(
        self,
        chessboard_monitor: "ChessboardMonitoringInterface",
        chessboard_player: "ChessboardPlayingInterface",
        chess_library: "ChessLibraryInterface",
        config: "ConfigInterface",
    ) -> None:
        self.chessboard_monitor = chessboard_monitor
        self.chessboard_player = chessboard_player
        self.chess_library = chess_library
        self.config = config

        self.currently_highlighted_squares: tuple[Square, Square] | None = None
        self.our_last_move: Move | None = None
        self.move_done_on_the_board: Move | None = None

        self.analysis = self.chess_library.get_current_analysis_result(0.01)

    def start_the_game(self) -> None:
        if not self.config.observer_only_mode:
            self._play_first_move_as_white_if_necessary()

        print("Starting to observe the board")
        while True:
            if self.config.should_sleep:
                time.sleep(self.config.sleep_interval_between_screenshots)
            try:
                self._look_at_the_chessboard_and_react_on_new_moves()
            except NoNewMoveFoundOnTheChessboard:
                continue
            except TheGameHasFinished:
                break

    def _play_first_move_as_white_if_necessary(self) -> None:
        if self.chess_library.should_start_as_white():
            print("Kicking the game by playing first")
            self._analyze_position_and_suggest_the_best_move()
            self._perform_the_best_move_on_the_screen_and_internally()

    def _look_at_the_chessboard_and_react_on_new_moves(self) -> None:
        self._get_currently_highlighted_squares()
        self._check_if_last_move_was_not_done_by_us()

        self._recognize_move_done_on_the_board()
        self._play_the_move_from_the_board_on_internal_board()

        self._check_if_the_game_did_not_finish()

        self._analyze_position_and_suggest_the_best_move()

        if not self.config.observer_only_mode:
            self._perform_the_best_move_on_the_screen_and_internally()

        self._check_if_the_game_did_not_finish()

    def _get_currently_highlighted_squares(self) -> None:
        whole_screen = get_screenshot()

        # Quick check if the previously highlighted squares are still
        #   highlighted - having to check only 2 squares instead of 64
        if self.currently_highlighted_squares:
            if self.chessboard_monitor.check_if_squares_are_highlighted(
                whole_screen=whole_screen,
                squares_to_check=self.currently_highlighted_squares,
            ):
                raise NoNewMoveFoundOnTheChessboard("Same highlight as before")

        # Getting highlighted squares as a sign of previous move
        highlighted_squares = self.chessboard_monitor.get_highlighted_squares(
            whole_screen
        )
        if len(highlighted_squares) != 2:
            raise NoNewMoveFoundOnTheChessboard("No highlight found")

        self.currently_highlighted_squares = (
            highlighted_squares[0],
            highlighted_squares[1],
        )

    def _check_if_last_move_was_not_done_by_us(self) -> None:
        if not self.our_last_move or not self.currently_highlighted_squares:
            return

        highlighted_move_is_ours = (
            self.our_last_move.from_square in self.currently_highlighted_squares
            and self.our_last_move.to_square in self.currently_highlighted_squares
        )
        if highlighted_move_is_ours:
            raise NoNewMoveFoundOnTheChessboard("Last move was ours")

    def _recognize_move_done_on_the_board(self) -> None:
        self.move_done_on_the_board = None

        assert self.currently_highlighted_squares
        possible_moves_from_highlight = [
            self.currently_highlighted_squares[0]
            + self.currently_highlighted_squares[1],
            self.currently_highlighted_squares[1]
            + self.currently_highlighted_squares[0],
        ]

        # Looping through all (2) possibilities of movement between the two
        #   highlighted squares, and determining, which one of them is a valid move
        for candidate_move in possible_moves_from_highlight:
            if self.chess_library.is_valid_move(candidate_move):
                print(f"New move on board - {self._format_move(candidate_move)}")
                self.move_done_on_the_board = candidate_move
                break

        # In ideal condition this should never happen, but in practice
        #   can, when these is some inconsistency (it did not catch some move)
        # TODO: move this corner case elsewhere
        if not self.move_done_on_the_board:
            print("No move was done - please investigate, why")
            print("MOST PROBABLY THE MOVE WAS NOT DONE ON THE SCREEN BY PYAUTOGUI")
            print("possible_moves_from_highlight", possible_moves_from_highlight)
            print("our_last_move", self.our_last_move)
            print("highlighted_squares", self.currently_highlighted_squares)
            raise NoNewMoveFoundOnTheChessboard("Something inconsistent happened")

    def _perform_the_best_move_on_the_screen_and_internally(self) -> None:
        if self.config.trigger_moves_manually:
            print(f"Waiting for trigger to play move: {self.config.keyboard_trigger}")
            wait_for_keyboard_trigger(self.config.keyboard_trigger)

        move = self.analysis.best_move
        self._do_the_move_on_screen_chessboard(move)
        self._play_move_on_our_internal_board(move)
        self.our_last_move = move

    def _do_the_move_on_screen_chessboard(self, move: Move) -> None:
        print(f"I AM PLAYING {self._format_move(move)}")

        # Playing the move on the screen chessboard
        # TODO: could have a check that the move was really performed
        #   on the screen - and if not - try to do it again
        self.chessboard_player.play_move(move)

    def _play_the_move_from_the_board_on_internal_board(self) -> None:
        if not self.move_done_on_the_board:
            return
        self._play_move_on_our_internal_board(self.move_done_on_the_board)

    def _play_move_on_our_internal_board(self, move: Move) -> None:
        # NOTE: we must first retrieve the move and only then push it one
        #   the board, otherwise the SAN representation would fail
        #   (it only takes valid moves in current situation)
        print(f"Playing move on our internal board: {self._format_move(move)}")
        self.chess_library.play_move(move)

    def _analyze_position_and_suggest_the_best_move(self) -> None:
        time_to_think = self._get_time_to_think_according_to_last_position()
        self.analysis = self.chess_library.get_current_analysis_result(time_to_think)
        print(f"{40*' '}Score: {self.analysis.mate_string or self.analysis.pawn_score}")
        if self.config.observer_only_mode:
            print(f"{40*' '}I would play {self._format_move(self.analysis.best_move)}")

    def _get_time_to_think_according_to_last_position(self) -> float:
        if (
            self.analysis.mate_string
            or self.analysis.pawn_score
            > self.config.pawn_threshold_when_already_winning
        ):
            return self.config.time_limit_to_think_when_already_winning
        elif self.analysis.pawn_score < self.config.pawn_threshold_when_losing:
            return self.config.time_limit_to_think_when_losing
        else:
            return self.config.time_limit_to_think_normal

    def _format_move(self, move: Move) -> str:
        return self.chess_library.get_notation_from_move(move)

    def _check_if_the_game_did_not_finish(self) -> None:
        if self.chess_library.is_game_over():
            self._evaluate_winner_and_finish_the_game()

    def _evaluate_winner_and_finish_the_game(self) -> None:
        outcome = self.chess_library.get_game_outcome()

        if outcome == ChessResult.Win:
            print("YOU HAVE WON, CONGRATULATIONS!!")
            raise TheGameHasFinished("You have won!")
        elif outcome == ChessResult.Lost:
            print("YOU HAVE LOST, MAYBE NEXT TIME!!")
            raise TheGameHasFinished("You have lost!")
        else:
            print("DRAW - WHAT A GAME!!")
            raise TheGameHasFinished("Draw!")
