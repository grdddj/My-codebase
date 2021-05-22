import pyautogui
from pynput import mouse

# Making all pyautogui actions faster, default is 0.1 seconds
pyautogui.PAUSE = 0.01


class HelpersToAssignChessboard:
    def __init__(self):
        self.chessboard_left_top_pixel = None
        self.chessboard_right_bottom_pixel = None

    def get_left_top_and_right_bottom_chessboard_pixels(self) -> tuple:
        print("Please rightlick the most upperleft corner of the chessboard")
        with mouse.Listener(
                on_click=self.assign_two_corners_on_click) as listener:
            listener.join()

        print("Boundaries assigned, you may want to save them into config.py")

        return (self.chessboard_left_top_pixel, self.chessboard_right_bottom_pixel)

    def stop_listening_on_mouse_input(self) -> bool:
        if self.chessboard_left_top_pixel is not None and self.chessboard_right_bottom_pixel is not None:
            print("stopping the assignment")
            return True
        return False

    def assign_two_corners_on_click(self, x: int, y: int, button, pressed: bool) -> bool:
        if button == mouse.Button.right and pressed:
            if self.chessboard_left_top_pixel is None:
                self.chessboard_left_top_pixel = (x, y)
                print("chessboard_left_top_pixel assigned - {},{}".format(x, y))
                print("Please rightlick the most bottomright corner of the chessboard")
            elif self.chessboard_right_bottom_pixel is None:
                self.chessboard_right_bottom_pixel = (x, y)
                print("chessboard_right_bottom_pixel assigned - {},{}".format(x, y))

        return not self.stop_listening_on_mouse_input()

    @staticmethod
    def create_dict_of_square_centers(
        chessboard_left_top_pixel: tuple,
        chessboard_right_bottom_pixel: tuple,
        our_colour: str
    ) -> dict:
        chessboard_size = chessboard_right_bottom_pixel[0] - chessboard_left_top_pixel[0]
        square_size = chessboard_size // 8

        # Constructing the dictionary of square centers
        # We must distinguish between playing white or black when doing that
        rows = "12345678"
        columns = "abcdefgh"
        square_centers_dict = {}

        for col_index, col in enumerate(columns):
            for row_index, row in enumerate(rows):
                coord = col + row
                if our_colour == "white":
                    center_x = chessboard_left_top_pixel[0] + (square_size // 2 + col_index * square_size)
                    center_y = chessboard_right_bottom_pixel[1] - (square_size // 2 + row_index * square_size)
                else:
                    center_x = chessboard_right_bottom_pixel[0] - (square_size // 2 + col_index * square_size)
                    center_y = chessboard_left_top_pixel[1] + (square_size // 2 + row_index * square_size)
                square_centers_dict[coord] = (center_x, center_y)

        return square_centers_dict


class HelpersToAnalyzeChessboard:
    @staticmethod
    def are_there_colours_in_a_PIL_image(
        PIL_image,
        colours_to_locate: list
    ) -> dict:
        # Getting the list of all colours in that image
        ocurrences_and_colours = PIL_image.getcolors(maxcolors=66666)

        # Trying to locate our wanted colour there
        for ocurrence, colour in ocurrences_and_colours:
            if colour in colours_to_locate:
                return {"is_there": True, "ocurrences": ocurrence}
        else:
            return {"is_there": False, "ocurrences": None}

    @staticmethod
    def get_highlighted_squares_from_picture(
        whole_screen,
        square_centers_dict: dict,
        square_size: int,
        highlighted_colours: list
    ) -> list:
        highlighted_squares = []

        # Defining how big part of a square will be cut out to allow for some
        #   inacurracies in square identification (so that the highlighted
        #   colours are really found only on two squares)
        square_boundary = 0.2
        square_boundary_pixels = square_size * square_boundary

        # Looping through all squares, and testing if they contain highlighted
        #   colour
        for key, value in square_centers_dict.items():
            left_top_x_square = value[0] - square_size // 2
            left_top_y_square = value[1] - square_size // 2
            corners_of_current_square = (
                left_top_x_square + square_boundary_pixels,
                left_top_y_square + square_boundary_pixels,
                left_top_x_square + square_size - square_boundary_pixels,
                left_top_y_square + square_size - square_boundary_pixels
            )
            square_image = whole_screen.crop(corners_of_current_square)
            are_there = HelpersToAnalyzeChessboard.are_there_colours_in_a_PIL_image(
                PIL_image=square_image,
                colours_to_locate=highlighted_colours
            )
            if are_there["is_there"]:
                highlighted_squares.append(key)

        return highlighted_squares

    @staticmethod
    def get_highlighted_squares_from_picture_kurnik(
        whole_screen,
        square_centers_dict: dict,
        square_size: int,
        highlighted_colours: list
    ) -> list:
        highlighted_squares = []

        # Defining how big part of a square will be cut out to allow for some
        #   inacurracies in square identification (so that the highlighted
        #   colours are really found only on two squares)
        square_boundary = 0
        square_boundary_pixels = square_size * square_boundary

        # Looping through all squares, and testing if they contain highlighted
        #   colour
        for key, value in square_centers_dict.items():
            left_top_x_square = value[0] - square_size // 2
            left_top_y_square = value[1] - square_size // 2
            corners_of_current_square = (
                left_top_x_square + square_boundary_pixels,
                left_top_y_square + square_boundary_pixels,
                left_top_x_square + square_size - square_boundary_pixels,
                left_top_y_square + square_size - square_boundary_pixels
            )
            square = whole_screen.crop(corners_of_current_square)

            # Creating four sub-squares, to test if the colour is present in
            #   at least three of them - which signs success
            length = square.size[0]
            step = length // 2
            sub_squares_corners = [
                (0, 0, step, step),
                (step, 0, step * 2, step),
                (0, step, step, step * 2),
                (step, step, step * 2, step * 2)
            ]

            found = 0
            for smaller_square_corners in sub_squares_corners:
                smaller_square_image = square.crop(smaller_square_corners)
                are_there = HelpersToAnalyzeChessboard.are_there_colours_in_a_PIL_image(
                    PIL_image=smaller_square_image,
                    colours_to_locate=highlighted_colours
                )
                if are_there["is_there"]:
                    found += 1

            if found > 2:
                highlighted_squares.append(key)

        return highlighted_squares

    @staticmethod
    def drag_mouse_from_square_to_square(
        square_centers_dict: dict,
        from_square: str,
        to_square: str
    ) -> None:
        initial_position = pyautogui.position()

        try:
            from_center = square_centers_dict[from_square]
        except KeyError:
            print(f"Coordination '{from_square}' does not exist!")
            return

        try:
            to_center = square_centers_dict[to_square]
        except KeyError:
            print(f"Coordination '{to_square}' does not exist!")
            return

        pyautogui.click(*from_center)
        pyautogui.click(*to_center)

        pyautogui.moveTo(*initial_position)
        pyautogui.click(*initial_position)
