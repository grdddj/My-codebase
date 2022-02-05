import os
import tkinter as tk
from tkinter import font

import requests

# Changeable parameters - the dimensions of main window
HEIGHT = 600
WIDTH = 700

TITLE = "Weather App"

# Parsing the weather object - a response from API
def format_response(weather):
    try:
        name = weather["name"]
        desc = weather["weather"][0]["description"]
        temp = weather["main"]["temp"]

        return_value = "City: {}\nDescription: {}\nTemperature: {} °C".format(
            name, desc, temp
        )
    except:
        return_value = "Sorry, there was a problem"

    return return_value


# Contacting the API with a chosen city and requesting current weather situation
def get_weather(city):
    API_KEY = "7a38a131f190c46ddcff256bf5c2d9d7"
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"APPID": API_KEY, "q": city, "units": "metric"}
    response = requests.get(url, params=params)
    weather = response.json()

    # Assigning the formatted response to the text of the label
    label["text"] = format_response(weather)


# Defining the main window and its title
root = tk.Tk()
root.title(TITLE)

# Getting the initial screen-size
canvas = tk.Canvas(root, height=HEIGHT, width=WIDTH)
canvas.pack()

# Setting the background image - if the image exists in the current dir
# Having an if-statement not to be dependant on it in the case of .exe file
if os.path.isfile("./background.png"):
    background_image = tk.PhotoImage(file="background.png")
    background_label = tk.Label(root, image=background_image)
    background_label.place(x=0, y=0, relwidth=1, relheight=1)

# Frame adjusts itself in the parent container
frame_top = tk.Frame(root, bg="#42b6f4", bd=5)  # Colors can ge also "blue", "red"...
frame_top.place(
    relx=0.5, rely=0.1, relwidth=0.7, relheight=0.1, anchor="n"
)  # Centering the frame
# .place() gives more flexibility than .pack() and .grid()
# It is nicely responsive with that relative stuff

entry = tk.Entry(frame_top, bg="orange", font=("Calibri", 15), bd=5)
entry.place(relx=0, rely=0, relheight=1, relwidth=0.7)
# entry.grid(row=0, column=2) # Used to show the widget
# entry.pack(side="left", fill="both") # Used to show the widget

button = tk.Button(
    frame_top,
    text="Search",
    bg="grey",
    fg="black",
    font=("Calibri", 15),
    command=lambda: get_weather(entry.get()),
)
button.place(relx=0.75, rely=0, relheight=1, relwidth=0.25)
# place(anchor="") - choosing the zero-point (NW, SE or other directions)
# button.grid(row=0, column=0) # Used to show the widget
# button.pack(side="left", fill="both", expand=True) # Used to show the widget
# pack(side="") - where it is (right, left, bottom, top (default))
# pack(fill="") - filling the parent (x, y, both, none (default))
# pack(expand="") - if it should expand (True, False (default))

frame_bottom = tk.Frame(
    root, bg="#42b6f4", bd=10
)  # Colors can ge also "blue", "red"...
frame_bottom.place(relx=0.5, rely=0.3, relwidth=0.7, relheight=0.6, anchor="n")

label = tk.Label(
    frame_bottom, bg="yellow", font=("Calibri", 25), anchor="nw", justify="left", bd=4
)
label.place(relheight=1, relwidth=1)
# label.grid(row=0, column=1) # Used to show the widget
# label.pack(side="left", fill="both") # Used to show the widget

root.mainloop()  # Used to end the area
