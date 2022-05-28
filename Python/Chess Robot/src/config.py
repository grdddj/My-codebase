from pathlib import Path

from pynput import keyboard

from .api import ConfigInterface

root_dir = Path(__file__).resolve().parent.parent


class Config(ConfigInterface):
    def __init__(
        self,
        observer_only_mode: bool = False,
        force_boundaries_update: bool = False,
        trigger_moves_manually: bool = False,
        website: str = "lichess",
        mode: str = "superblitz",
        debug: bool = False,
    ) -> None:
        self.observer_only_mode = observer_only_mode
        self.force_boundaries_update = force_boundaries_update
        self.trigger_moves_manually = trigger_moves_manually
        self.website = website
        self.mode = mode
        self.debug = debug

        # Stockfish engine downloaded at https://stockfishchess.org/download/
        self.engine_location = str(Path(root_dir / "engines" / "stockfish_15_x64_bmi2"))

        # How many seconds to analyze before suggesting a move
        if self.mode == "superblitz":
            self.time_limit_to_think_normal = 0.01
            self.time_limit_to_think_when_already_winning = 0.005
            self.time_limit_to_think_when_losing = 0.1
        elif self.mode == "blitz":
            self.time_limit_to_think_normal = 0.1
            self.time_limit_to_think_when_already_winning = 0.05
            self.time_limit_to_think_when_losing = 1
        elif self.mode == "slow":
            self.time_limit_to_think_normal = 1
            self.time_limit_to_think_when_already_winning = 0.5
            self.time_limit_to_think_when_losing = 5
        else:
            raise ValueError(f"Invalid mode {self.mode}")

        # When to consider we are winning or losing (to adjust think time)
        self.pawn_threshold_when_already_winning = 3.0
        self.pawn_threshold_when_losing = -0.5

        # How long to pause between watching again at the chessboard
        self.should_sleep = False
        self.sleep_interval_between_screenshots = 0.01

        # Allowing for keyboard-triggered moves (instead of automatic)
        self.keyboard_trigger = keyboard.Key.ctrl_r

        ###########################################
        # PART ABOUT THE COORDINATES AND COLOURS - website dependent
        ###########################################

        if self.website == "lichess":
            # https://lichess.org/analysis/standard
            # https://lichess.org/mi1YjKcg
            self.chessboard_left_top_pixel = (541, 225)
            self.chessboard_right_bottom_pixel = (1164, 854)
            self.white_field_highlight_colour = (205, 210, 106)
            self.black_field_highlight_colour = (170, 162, 58)
        elif self.website == "chess.com":
            # https://www.chess.com/cs/play/computer
            self.chessboard_left_top_pixel = (334, 272)
            self.chessboard_right_bottom_pixel = (966, 903)
            self.white_field_highlight_colour = (247, 247, 105)
            self.black_field_highlight_colour = (187, 203, 43)
        elif self.website == "kurnik":
            # https://www.playok.com/cs/sachy/
            self.chessboard_left_top_pixel = (341, 205)
            self.chessboard_right_bottom_pixel = (1107, 970)
            self.white_field_highlight_colour = (47, 66, 45)
            self.black_field_highlight_colour = (17, 53, 20)
        else:
            raise ValueError(f"Unknown website: {self.website}")
