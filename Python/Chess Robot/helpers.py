from typing import Dict, List, Tuple

import pyautogui  # type: ignore
from PIL import Image  # type: ignore
from pynput import mouse  # type: ignore

# Making all pyautogui actions faster, default is 0.1 seconds
pyautogui.PAUSE = 0.01

Pixel = Tuple[int, int]
SquareCenterDict = Dict[str, Pixel]
ColorValue = Tuple[int, int, int]


class HelpersToAssignChessboard:
    def __init__(self):
        self.chessboard_left_top_pixel = None
        self.chessboard_right_bottom_pixel = None

    def get_left_top_and_right_bottom_chessboard_pixels(self) -> Tuple[Pixel, Pixel]:
        print("Please rightlick the most upperleft corner of the chessboard")
        with mouse.Listener(on_click=self.assign_two_corners_on_click) as listener:
            listener.join()

        print("Boundaries assigned, you may want to save them into config.py")

        assert self.chessboard_left_top_pixel is not None
        assert self.chessboard_right_bottom_pixel is not None
        return self.chessboard_left_top_pixel, self.chessboard_right_bottom_pixel

    def assign_two_corners_on_click(
        self, x: int, y: int, button, pressed: bool
    ) -> bool:
        if button == mouse.Button.right and pressed:
            if self.chessboard_left_top_pixel is None:
                self.chessboard_left_top_pixel = (x, y)
                print(f"chessboard_left_top_pixel assigned - {x},{y}")
                print("Please rightlick the most bottomright corner of the chessboard")
            elif self.chessboard_right_bottom_pixel is None:
                self.chessboard_right_bottom_pixel = (x, y)
                print(f"chessboard_right_bottom_pixel assigned - {x},{y}")

        return not self.stop_listening_on_mouse_input()

    def stop_listening_on_mouse_input(self) -> bool:
        if (
            self.chessboard_left_top_pixel is not None
            and self.chessboard_right_bottom_pixel is not None
        ):
            print("Stopping the assignment")
            return True
        return False

    @staticmethod
    def create_dict_of_square_centers(
        chessboard_left_top_pixel: Pixel,
        chessboard_right_bottom_pixel: Pixel,
        our_colour: str,
    ) -> SquareCenterDict:
        chessboard_size = (
            chessboard_right_bottom_pixel[0] - chessboard_left_top_pixel[0]
        )
        square_size = chessboard_size // 8

        # Constructing the dictionary of square centers
        # We must distinguish between playing white or black when doing that
        rows = "12345678"
        columns = "abcdefgh"
        square_centers_dict: SquareCenterDict = {}

        for col_index, col in enumerate(columns):
            for row_index, row in enumerate(rows):
                coord = col + row
                if our_colour == "white":
                    center_x = chessboard_left_top_pixel[0] + (
                        square_size // 2 + col_index * square_size
                    )
                    center_y = chessboard_right_bottom_pixel[1] - (
                        square_size // 2 + row_index * square_size
                    )
                else:
                    center_x = chessboard_right_bottom_pixel[0] - (
                        square_size // 2 + col_index * square_size
                    )
                    center_y = chessboard_left_top_pixel[1] + (
                        square_size // 2 + row_index * square_size
                    )
                square_centers_dict[coord] = (center_x, center_y)

        return square_centers_dict


class HelpersToAnalyzeChessboard:
    def __init__(
        self,
        square_centers_dict: SquareCenterDict,
        square_size: int,
        highlighted_colours: List[ColorValue],
    ):
        self.square_centers_dict = square_centers_dict
        self.square_size = square_size
        self.highlighted_colours = highlighted_colours

    def get_highlighted_squares_from_picture(
        self, whole_screen: Image.Image
    ) -> List[str]:
        highlighted_squares: List[str] = []

        # TODO: should crop the image for just the chessboard area
        #   so that it can save some time manipulating with smaller image

        # Looping through all squares, and testing if they contain highlighted
        #   colour
        for square, square_center_coords in self.square_centers_dict.items():
            is_highlighted = self.check_if_square_is_highlighted(
                whole_screen=whole_screen, square_center_coords=square_center_coords
            )
            if is_highlighted:
                highlighted_squares.append(square)

            # Exiting when we have found two squares, there should not be more
            if len(highlighted_squares) == 2:
                break

        return highlighted_squares

    def check_if_square_is_highlighted(
        self, whole_screen: Image.Image, square_center_coords: Pixel
    ) -> bool:
        # Defining how big part of a square will be cut out to allow for some
        #   inacurracies in square identification (so that the highlighted
        #   colours are really found only on two squares)
        square_boundary = 0.2
        square_boundary_pixels = int(self.square_size * square_boundary)

        left_top_x_square = square_center_coords[0] - self.square_size // 2
        left_top_y_square = square_center_coords[1] - self.square_size // 2
        corners_of_current_square = (
            left_top_x_square + square_boundary_pixels,
            left_top_y_square + square_boundary_pixels,
            left_top_x_square + self.square_size - square_boundary_pixels,
            left_top_y_square + self.square_size - square_boundary_pixels,
        )
        square_image = whole_screen.crop(corners_of_current_square)
        is_highlighted = HelpersToAnalyzeChessboard.are_there_colours_in_a_PIL_image(
            PIL_image=square_image, colours_to_locate=self.highlighted_colours
        )

        return is_highlighted

    def check_if_squares_are_highlighted(
        self, whole_screen: Image.Image, squares_to_check: List[str]
    ) -> bool:
        square_centers_to_check = [
            square_center_coords
            for square, square_center_coords in self.square_centers_dict.items()
            if square in squares_to_check
        ]

        for square_center_coords in square_centers_to_check:
            is_highlighted = self.check_if_square_is_highlighted(
                whole_screen=whole_screen, square_center_coords=square_center_coords
            )
            if not is_highlighted:
                return False

        return True

    def get_highlighted_squares_from_picture_kurnik(
        self, whole_screen: Image.Image
    ) -> List[str]:
        highlighted_squares: List[str] = []

        # Defining how big part of a square will be cut out to allow for some
        #   inacurracies in square identification (so that the highlighted
        #   colours are really found only on two squares)
        square_boundary = 0
        square_boundary_pixels = self.square_size * square_boundary

        # Looping through all squares, and testing if they contain highlighted
        #   colour
        for square, center_coords in self.square_centers_dict.items():
            left_top_x_square = center_coords[0] - self.square_size // 2
            left_top_y_square = center_coords[1] - self.square_size // 2
            corners_of_current_square = (
                left_top_x_square + square_boundary_pixels,
                left_top_y_square + square_boundary_pixels,
                left_top_x_square + self.square_size - square_boundary_pixels,
                left_top_y_square + self.square_size - square_boundary_pixels,
            )
            square_image = whole_screen.crop(corners_of_current_square)

            # Creating four sub-squares, to test if the colour is present in
            #   at least three of them - which signs success
            length = square_image.size[0]
            step = length // 2
            sub_squares_corners = [
                (0, 0, step, step),
                (step, 0, step * 2, step),
                (0, step, step, step * 2),
                (step, step, step * 2, step * 2),
            ]

            found = 0
            for smaller_square_corners in sub_squares_corners:
                smaller_square_image = square_image.crop(smaller_square_corners)
                are_there = HelpersToAnalyzeChessboard.are_there_colours_in_a_PIL_image(
                    PIL_image=smaller_square_image,
                    colours_to_locate=self.highlighted_colours,
                )
                if are_there:
                    found += 1

            if found > 2:
                highlighted_squares.append(square)

            # Exiting when we have found two squares, there should not be more
            if len(highlighted_squares) == 2:
                break

        return highlighted_squares

    def drag_mouse_from_square_to_square(
        self, from_square: str, to_square: str
    ) -> None:
        initial_mouse_position = pyautogui.position()

        try:
            from_square_center = self.square_centers_dict[from_square]
        except KeyError:
            print(f"Coordination '{from_square}' does not exist!")
            return

        try:
            to_square_center = self.square_centers_dict[to_square]
        except KeyError:
            print(f"Coordination '{to_square}' does not exist!")
            return

        pyautogui.click(*from_square_center)
        pyautogui.click(*to_square_center)

        pyautogui.moveTo(*initial_mouse_position)
        pyautogui.click(*initial_mouse_position)

    def click_on_square(self, square: str) -> None:
        try:
            square_center = self.square_centers_dict[square]
        except KeyError:
            print(f"Coordination '{square}' does not exist!")
            return

        pyautogui.click(*square_center)

    @staticmethod
    def are_there_colours_in_a_PIL_image(
        PIL_image: Image.Image, colours_to_locate: List[ColorValue]
    ) -> bool:
        # TODO: faster approach could be just to check every nth (5th) pixel
        #   for being the colour we want, and return as soon as we find it

        # Getting the list of all colours in that image
        ocurrences_and_colours = PIL_image.getcolors(maxcolors=1024)

        # Trying to locate our wanted colour there
        for ocurrence, colour in ocurrences_and_colours:
            if colour in colours_to_locate:
                return True
        else:
            return False
