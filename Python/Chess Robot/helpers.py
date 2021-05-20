import pyautogui
from pynput import mouse


class HelpersToAssignChessboard:
    def __init__(self):
        self.left_top = None
        self.right_bottom = None

    def get_left_top_and_right_bottom(self) -> tuple:
        print("Please rightlick the most upperleft corner of the chessboard")
        with mouse.Listener(
                on_click=self.on_click) as listener:
            listener.join()

        return (self.left_top, self.right_bottom)

    def stop_listening_on_mouse_input(self):
        if self.left_top is not None and self.right_bottom is not None:
            print("stopping the assignment")
            return True
        return False

    def on_click(self, x, y, button, pressed):
        if self.stop_listening_on_mouse_input():
            return False
        if button == mouse.Button.right and pressed:
            if self.left_top is None:
                self.left_top = (x, y)
                print("left_top assigned - {},{}".format(x, y))
                print("Please rightlick the most bottomright corner of the chessboard")
            elif self.right_bottom is None:
                self.right_bottom = (x, y)
                print("right_bottom assigned - {},{}".format(x, y))

    @staticmethod
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
        square_boundary = 0.2
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
                (0, 0, step, step),
                (step, 0, step * 2, step),
                (0, step, step, step * 2),
                (step, step, step * 2, step * 2)
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

    def drag_mouse_from_square_to_square(square_centers, from_square, to_square):
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
