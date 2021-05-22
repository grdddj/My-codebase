"""
Cloned robot that is just observing the board and evaluating
    the position and suggesting best moves

Possible improvements:
- listen for certain keys when being turned on and off, so we do not have
    to leave the mouse from playing window (which is visible to oponent)
- needs a protection against "premove" - when the opponent fires a move
    immediately after we play - and program cannot recognize two moves
    happened at once
"""

from chess_robot import ChessRobot

if __name__ == "__main__":
    while True:
        try:
            robot = ChessRobot(observer_only_mode=True)
            robot.start_the_game()
        except KeyboardInterrupt:
            print("Thank you for the games!")
            break
