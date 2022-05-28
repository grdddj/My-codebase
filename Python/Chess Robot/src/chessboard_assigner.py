from __future__ import annotations

from typing import TYPE_CHECKING

from pynput import mouse

from .api import ChessboardAssignerInterface

if TYPE_CHECKING:  # pragma: no cover
    from .helpers import Pixel


class ChessboardAssigner(ChessboardAssignerInterface):
    def __init__(self) -> None:
        self._left_top: "Pixel" | None = None
        self._right_bottom: "Pixel" | None = None

    def get_left_top_and_right_bottom_chessboard_pixels(
        self,
    ) -> tuple["Pixel", "Pixel"]:
        """Returns boundaries of the chessboard"""
        print("Please rightlick the most upperleft corner of the chessboard")
        with mouse.Listener(on_click=self._assign_two_corners_on_click) as listener:
            listener.join()

        print("Boundaries assigned, you may want to save them into config.py")

        assert self._left_top is not None
        assert self._right_bottom is not None
        return self._left_top, self._right_bottom

    def _assign_two_corners_on_click(
        self, x: int, y: int, button, pressed: bool
    ) -> bool:
        """Listen for right-clicks and assign the two corners"""
        if button == mouse.Button.right and pressed:
            if self._left_top is None:
                self._left_top = (x, y)
                print(f"chessboard_left_top_pixel assigned - {x},{y}")
                print("Please rightlick the most bottomright corner of the chessboard")
            elif self._right_bottom is None:
                self._right_bottom = (x, y)
                print(f"chessboard_right_bottom_pixel assigned - {x},{y}")

        return not self._stop_listening_on_mouse_input()

    def _stop_listening_on_mouse_input(self) -> bool:
        """Stop whenever both corners are assigned"""
        if self._left_top is not None and self._right_bottom is not None:
            print("Stopping the assignment")
            return True
        return False
