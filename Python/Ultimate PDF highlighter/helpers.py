"""
This file stores hepler functions to enable PDF highlight scripts run smoothly
    without the main code being polluted with unnecessary logic.
"""

import pyautogui

class Helpers:
    @staticmethod
    def _get_position_of_object(object_image_location: str,
                               confidence_of_locating: float = 1,
                               coords_and_square_size: dict = None) -> dict:
        """
        Determines the position of a certain object on the screen.
        When we suspect the object will be around a certain location,
            we can input dictionary with these data, and it will
            first investigate this smaller location - thus making
            the search possibly quicker that searching in the whole screen

        Using None as a default argument, because using empty dictionary is bad:
        - https://docs.quantifiedcode.com/python-anti-patterns/correctness/mutable_default_value_as_argument.html
        """

        # Trying to locate the object in the vicinity of current position (if wanted)
        if coords_and_square_size is not None:
            # Getting the coordination of the region
            region_where_to_look = Helpers.__safely_create_square_region_on_the_screen(
                x_coord=coords_and_square_size["x_coord"],
                y_coord=coords_and_square_size["y_coord"],
                square_size=coords_and_square_size["square_size"],
                screen_size=pyautogui.size())

            # Trying to locate the object in a small region
            position_of_object = pyautogui.locateOnScreen(
                object_image_location,
                region=region_where_to_look)

            # If we managed to find the object in the smaller region, return it
            # Otherwise the object will be searched for on the whole screen
            if position_of_object:
                return {"found": True, "coords": position_of_object}

        # Locating the object on the whole screen (after first trial failed
        #   or was not even wanted)
        position_of_object = pyautogui.locateOnScreen(
            object_image_location)

        return {"found": position_of_object is not None,
                "coords": position_of_object}

    @staticmethod
    def __safely_create_square_region_on_the_screen(x_coord: int,
                                                    y_coord: int,
                                                    square_size: int,
                                                    screen_size: tuple,
                                                    region_type: str = "pyautogui") -> tuple:
        """
        Determines a square region on the screen, that has a defined square size
            and is surrounding the point with given x and y coordinates.
        It tries to put the point in the middle of the square, but when the
            point is close to screen boundary, it is not possible - in this case
            it returns still the same-sized square, but fully located on
            the screen.
        """

        # There are two possibilities of returning the result:
        # Pyautogui needs format (x_upper_left_corner, y_upper_left_corner,
        #   x_rectangle_length, y_rectangle_length), whereas PIL demands
        #   (x_upper_left_corner, y_upper_left_corner, x_bottom_right_corner,
        #   y_bottom_right_corner)
        assert(region_type in ["pyautogui", "PIL"])

        # Finding out the resolution of the screen, to righly construct the square
        x_screen_size, y_screen_size = screen_size

        # Guard against square sizes bigger than the whole screen
        assert(square_size <= x_screen_size and square_size <= y_screen_size)

        # Calculating the coordinates of ideal top-left square corner
        x_corner = int(x_coord - square_size / 2)
        y_corner = int(y_coord - square_size / 2)

        # Transforming the possibly negative coordinates to non-negative,
        #   as negative coordinations do not exist
        x_corner = x_corner if x_corner > -1 else 0
        y_corner = y_corner if y_corner > -1 else 0

        # Identifying if the square would be outside the screen, and if so,
        #   adjust the corner further from the border, to fix this
        if x_corner + square_size >= x_screen_size:
            x_corner = x_screen_size - square_size - 1
        if y_corner + square_size >= y_screen_size:
            y_corner = y_screen_size - square_size - 1

        # Last sanity check before returning
        assert(0 <= x_corner < x_screen_size - square_size)
        assert(0 <= y_corner < y_screen_size - square_size)

        if region_type == "pyautogui":
            return (x_corner, y_corner, square_size, square_size)
        elif region_type == "PIL":
            return(x_corner, y_corner, x_corner + square_size, y_corner + square_size)

    @staticmethod
    def _locate_pixel_in_the_image(PIL_image,
                                   colour_to_match: tuple,
                                   x_coord: int,
                                   y_coord: int,
                                   square_size: int,
                                   pixels_to_skip_on_margin_if_possible: int,
                                   grid_size_when_searching: int) -> dict:
        """
        Searching the image for a certain pixel, according to supplied
            colour.
        At the beginning smaller area around a certain point is searched,
            as there is the highest chance of locating what we want.
        """

        # First checking if the pixel colour to match really exists in the image
        # In the negative case immediately return that there is nothing
        is_there_my_colour = Helpers.__is_there_a_colour_in_a_PIL_image(
            PIL_image=PIL_image,
            colour_to_locate=colour_to_match)

        if not is_there_my_colour["is_there"]:
            return {"should_i_click": False, "coords": None}

        # There is a high chance the mouse will be already pointing at
        #   our desired pixel, so before investigating bigger picture
        #   try to see if we are not already there
        if PIL_image.getpixel((x_coord, y_coord)) == colour_to_match:
            return {"should_i_click": True, "coords": (x_coord, y_coord)}

        # If we are not so lucky, we have to examine the image more thoroughly
        # Getting the coordination of our region in vicinity of cursor
        region_where_to_look = Helpers.__safely_create_square_region_on_the_screen(
            x_coord=x_coord,
            y_coord=y_coord,
            square_size=square_size,
            screen_size=PIL_image.size,
            region_type="PIL")

        # Trying to locate our colour in our region
        is_there_colour_in_region = Helpers.__is_there_a_colour_in_a_PIL_image(
            PIL_image=PIL_image.crop(box=region_where_to_look),
            colour_to_locate=colour_to_match)

        # If we manage to locate it in our smaller region, locate it there
        if is_there_colour_in_region["is_there"]:
            x_values_list = Helpers.__generate_list_from_range_starting_in_the_middle(
                lower_end=region_where_to_look[0],
                higher_end=region_where_to_look[2],
                step=grid_size_when_searching)

            for x_value in x_values_list:
                analyze_y_axis = Helpers._search_the_y_axis_for_pixel(
                    PIL_image=PIL_image,
                    colour_to_match=colour_to_match,
                    x_coord=x_value,
                    y_coord_current=y_coord,
                    distance_to_search=square_size,
                    pixels_to_skip_on_margin_if_possible=pixels_to_skip_on_margin_if_possible)

                if analyze_y_axis["success"]:
                    return {"should_i_click": True, "coords": analyze_y_axis["coords"]}
        # If it is not in out smaller region, we must find it in the whole image
        else:
            # Starting with the current grid size, and if we are not successful
            #   divide it by two, so at the end we really examine all the pixels
            while grid_size_when_searching // 2 > 0:
                x_values_list = Helpers.__generate_list_from_range_starting_in_the_middle(
                    lower_end=0,
                    higher_end=PIL_image.size[0] - 1,
                    step=grid_size_when_searching)

                y_coord_in_the_middle = PIL_image.size[1] // 2

                for x_value in x_values_list:
                    analyze_y_axis = Helpers._search_the_y_axis_for_pixel(
                        PIL_image=PIL_image,
                        colour_to_match=colour_to_match,
                        x_coord=x_value,
                        y_coord_current=y_coord_in_the_middle,
                        distance_to_search=PIL_image.size[1],
                        pixels_to_skip_on_margin_if_possible=pixels_to_skip_on_margin_if_possible)

                    if analyze_y_axis["success"]:
                        return {"should_i_click": True, "coords": analyze_y_axis["coords"]}

                grid_size_when_searching = grid_size_when_searching // 2

        # It should never reach this assert, because the colour was identified
        #   in the image, and in the end we searched it pixel by pixel, so
        #   something must have gone wrong
        assert False

    @staticmethod
    def __generate_list_from_range_starting_in_the_middle(
            lower_end: int,
            higher_end: int,
            step: int,
            first_direction_from_middle: str = None) -> list:
        """
        Generates a list of numbers starting at the middle of the range
            and continuing gradually to the edges
        """

        assert(lower_end < higher_end)
        assert(step > 0)
        assert(first_direction_from_middle in [None, "up", "down", "mixed"])

        middle_point = int((lower_end + higher_end) / 2)

        bottom_part = []
        middle_part = [middle_point]
        upper_part = []

        # Filling the bottom part
        current_point = middle_point
        while current_point > lower_end:
            current_point -= step
            if current_point > lower_end:
                bottom_part.append(current_point)
            else:
                bottom_part.append(lower_end)

        # Filling the upper part
        current_point = middle_point
        while current_point < higher_end:
            current_point += step
            if current_point < higher_end:
                upper_part.append(current_point)
            else:
                upper_part.append(higher_end)

        # Starting from the middle position, and serving other parts
        #   according to the wanted direction
        # First going through the bottom part
        if first_direction_from_middle in [None, "down"]:
            resulting_list = middle_part + bottom_part + upper_part
        # First going through the upper part
        elif first_direction_from_middle == "up":
            resulting_list = middle_part + upper_part + bottom_part
        # When there should be mixed direction, taking gradually elements
        #   from both the bottom and upper part, until they are both
        #   exhausted
        elif first_direction_from_middle == "mixed":
            mixed_list = []
            max_length = max(len(bottom_part), len(upper_part))
            for index in range(max_length):
                try:
                    mixed_list.append(bottom_part[index])
                except IndexError:
                    pass
                try:
                    mixed_list.append(upper_part[index])
                except IndexError:
                    pass
            resulting_list = middle_part + mixed_list

        return resulting_list

    @staticmethod
    def _search_the_y_axis_for_pixel(PIL_image,
                                     colour_to_match: tuple,
                                     x_coord: int,
                                     y_coord_current: int,
                                     distance_to_search: int,
                                     pixels_to_skip_on_margin_if_possible: int = 0) -> dict:
        """
        Examining the given image for a certain pixel on a specific "x"
            coordination.
        Starting at the certain point and explore both directions, with
            the upward (decreasing "y" coordination) direction at first
        """

        screen_x_size, screen_y_size = PIL_image.size

        # Determining the ideal boundaries in which to locate the pixel
        y_low_boundary = int(y_coord_current - distance_to_search / 2)
        y_high_boundary = int(y_coord_current + distance_to_search / 2)

        # Transforming the possibly negative y_low_boundary to non-negative,
        #   as negative coordinations do not exist
        if y_low_boundary < 0:
            y_low_boundary = 0

        # Identifying if the y_high_boundary would be outside the screen,
        #    and if so, adjust it
        if y_high_boundary >= screen_y_size:
            y_high_boundary = screen_y_size - 1

        # We are "guessing" the most probable position of match is upwards
        #   on the screen, so create the interval to search accordingly
        upward_direction = list(range(y_coord_current, y_low_boundary, -1))
        downward_direction = list(range(y_coord_current, y_high_boundary))
        y_coords = upward_direction + downward_direction

        # Running the searches - depending on whether we want to skip the
        #   first n pixels on the margin, not to conflict with anything
        # EXAMPLE: When there is already some highlighted text between
        #   the newly highlighted text and the direction we are approaching this,
        #   the already highlighted one is activated when we click on the
        #   very margin - and we do not want that
        # Therefore we will continue for couple pixels in the same direction
        #   before searching again, and hopefully click there
        if pixels_to_skip_on_margin_if_possible < 1:
            for y_coord in y_coords:
                pixel = (x_coord, y_coord)
                if PIL_image.getpixel(pixel) == colour_to_match:
                    return {"success": True, "coords": pixel}
        else:
            margin_pixel_position = None
            counter_of_skipped_pixels = 0
            margin_found = False

            for y_coord in y_coords:
                pixel = (x_coord, y_coord)
                # If we have not located anything, search for the margin
                if not margin_found:
                    if PIL_image.getpixel(pixel) == colour_to_match:
                        margin_pixel_position = pixel
                        margin_found = True
                # When the margin is already located, skip next n pixels
                else:
                    if counter_of_skipped_pixels < pixels_to_skip_on_margin_if_possible:
                        counter_of_skipped_pixels += 1
                    else:
                        if PIL_image.getpixel(pixel) == colour_to_match:
                            return {"success": True, "coords": pixel}

            # If we found margin, but nothing else after those pixels to skip,
            #   return the margin at least
            if margin_pixel_position is not None:
                return {"success": True, "coords": margin_pixel_position}

        # If nothing was ever found, return negative results
        return {"success": False, "coords": None}

    @staticmethod
    def __is_there_a_colour_in_a_PIL_image(PIL_image,
                                           colour_to_locate: tuple) -> dict:
        """
        Determining whether colour is located in a PIL image
            (whether at least one pixel has this specific colour)
        It is surprisingly quick, 1920*1080 image with 12,000
            colours can identify arbitrary colour there in 0.02 seconds
        """

        # Getting the list of all colours in that image
        ocurrences_and_colours = PIL_image.getcolors(maxcolors=66666)

        # Trying to locate our wanted colour there
        for ocurrence, colour in ocurrences_and_colours:
            if colour == colour_to_locate:
                return {"is_there": True, "ocurrences": ocurrence}
        else:
            return {"is_there": False, "ocurrences": None}
