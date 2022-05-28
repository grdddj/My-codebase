from src.helpers import get_piece_colour, wait_to_trigger_the_game
from src.object_builder import get_config, get_robot

if __name__ == "__main__":
    config = get_config()

    print("Be sure to play on your main screen")
    while True:
        try:
            our_piece_colour = get_piece_colour()
            robot = get_robot(config, our_piece_colour)

            wait_to_trigger_the_game()

            robot.start_the_game()
        except KeyboardInterrupt:
            print("Thank you for the games!")
            break
