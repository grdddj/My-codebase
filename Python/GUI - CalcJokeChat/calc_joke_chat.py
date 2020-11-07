import tkinter as tk

from joke import Jokes
from chat import SupportWindow
from calc import CalculatorGUI

# TODO: "Answer to" functionality
# TODO: tell apart the messages of User vs Support - different colours etc.
# TODO: have some spacing between the messages (or right-left side)
# TODO: translation capabilities (like Lorcan's chatbot)
# TODO: allow for sharing pictures and files
# TODO: think about the sizing of the chat - so the words are not cut at the end of line
#   hardcode the window size and limit the characters
# TODO: emoticons
# TODO: thumbs up or other one-click symbol
# TODO: having a mood
# TODO: storing the whole user profile
# TODO: showing if somebody is on/offline
# TODO: websocket!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#   however, not sure how it would work with only one-thread Tkinter
# TODO: creating a better app in PyQt5?
# TODO: issue some alerts on there
# TODO: have gifts (for money)
# TODO: implement some points for each message
# TODO: notification about incoming message
#   - voice signal - play mp3 or wav, which can be packed together with app
# TODO: "Seen" of the message
# TODO: Show that somebody is typing
# TODO: autocorrect, aka Grammarly
# TODO: machine learning determining the tone of conversation (or topic)
# TODO: predefined answers
# TODO: random questions
# TODO: some place for message, or popup, that can be controlled remotely for notifications
# TODO: what is new button
# TODO: flashing buttons instead of popups that something is new


if __name__ == "__main__":
    root = tk.Tk()
    CalculatorGUI(root, Jokes, SupportWindow)
    root.eval('tk::PlaceWindow . center')
    root.mainloop()
