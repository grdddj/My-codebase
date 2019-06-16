import tkinter as tk
from tkinter import font
import requests
import os

# Changeable parameters - the dimensions of main window
HEIGHT = 600
WIDTH = 700

TITLE = "Chatting App"

# Filling the list of contacts
def populate_name():
    name_label['text'] = 'George'

# Filling the list of contacts
def populate_mood():
    mood_label['text'] = 'I have a good mood'

# Filling the list of contacts
def populate_contacts():
    contact_label['text'] = 'Guy1\nGuy2\nGuy3'

# Reading the content of a file and filling the appropriate text field
def populate_messages():
    with open('messages.txt', 'r') as file:
        content = file.read()
        messaging_label["state"] = "normal" # enabling to manipulate its content
        messaging_label.delete("1.0", "end") # deleting the old content
        messaging_label.insert("insert", content) # adding the new content
        messaging_label["state"] = "disabled" # disabling the content for user manipulation
        messaging_label.yview_moveto(1) # scrolling the scrollbar to the very bottom

# Sending a message - saving it to the text file
def send_message(message):
    try:
        # Appending the file with "a+" mode
        with open('messages.txt', 'a+') as file:
            file.write(message + "\n")
    except:
        return_value = "Sorry, there was a problem"
        return

    messaging_text.delete("1.0", "end")
    populate_messages()

def show_settings():
    print("show settings")

def edit_mood():
    print("edit_mood")

def add_contacts():
    print("add_contacts")

# Defining the main window and its title
root = tk.Tk()
root.title(TITLE)

# Getting the initial screen-size
canvas = tk.Canvas(root, height=HEIGHT, width=WIDTH)
canvas.pack()

# Setting the background image - if the image exists in the current dir
# Having an if-statement not to be dependant on it in the case of .exe file
if os.path.isfile('./background.png'):
    background_image = tk.PhotoImage(file="background.png")
    background_label = tk.Label(root, image=background_image)
    background_label.place(x=0, y=0, relwidth=1, relheight=1)


# Frame adjusts itself in the parent container
profile_area = tk.Frame(root, bg="#42b6f4", bd=5)
profile_area.place(relx=0.05, rely=0.1, relwidth=0.45, relheight=0.15)

name_label = tk.Label(profile_area, bg="yellow", font=("Calibri", 15), anchor="nw", justify="left", bd=4)
name_label.place(rely=0, relheight=0.5, relwidth=0.75)

mood_label = tk.Label(profile_area, bg="yellow", font=("Calibri", 15), anchor="nw", justify="left", bd=4)
mood_label.place(rely=0.5, relheight=0.5, relwidth=0.75)

settings_button = tk.Button(profile_area, text="Settings", bg="grey", fg="black", font=("Calibri", 10), justify="right", command=lambda: show_settings())
settings_button.place(relx=0.75, rely=0, relheight=0.5, relwidth=0.25)

mood_button = tk.Button(profile_area, text="Edit mood", bg="grey", fg="black", font=("Calibri", 10), justify="right", command=lambda: edit_mood())
mood_button.place(relx=0.75, rely=0.5, relheight=0.5, relwidth=0.25)


messaging_area = tk.Frame(root, bg="#42b6f4", bd=10)
messaging_area.place(relx=0.3, rely=0.3, relwidth=0.65, relheight=0.6)

scrollbar = tk.Scrollbar(messaging_area)
scrollbar.place(relx=0.95, relheight=0.8, relwidth=0.05)
#
# messaging_label = tk.Label(messaging_area, text="messages", bg="yellow", font=("Calibri", 15), anchor="nw", justify="left", bd=4, yscrollcommand=scrollbar.set)
# messaging_label.place(relheight=0.8, relwidth=1)
#
# scrollbar.config( command = messaging_label.yview )

# messaging_label = tk.Entry(messaging_area, textvariable=messages, bg="yellow", font=("Calibri", 15), state='readonly', bd=4)
# messaging_label = tk.Entry(messaging_area, textvariable=messages, bg="yellow", font=("Calibri", 15), bd=4)
messaging_label = tk.Text(messaging_area, bg="yellow", font=("Calibri", 15), state="disabled", bd=4, yscrollcommand=scrollbar.set)
messaging_label.place(relheight=0.8, relwidth=0.95)

scrollbar.config( command = messaging_label.yview )
# scrollbar.set("last")

messaging_text = tk.Text(messaging_area, bg="orange", font=("Calibri", 15), bd=5)
messaging_text.place(relx=0, rely=0.8, relheight=0.2, relwidth=0.8)

messaging_button = tk.Button(messaging_area, text="Send", bg="grey", fg="black", font=("Calibri", 10), justify="center", command=lambda: send_message(messaging_text.get("1.0", "end-1c")))
messaging_button.place(relx=0.8, rely=0.8,relheight=0.2, relwidth=0.2)

# scrollbar = tk.Scrollbar(messaging_label)
# scrollbar.pack( side='right', fill='y')



contacts_area = tk.Frame(root, bg="#42b6f4", bd=10)
contacts_area.place(relx=0.05, rely=0.3, relwidth=0.2, relheight=0.6)

contact_label = tk.Label(contacts_area, text="contacts", bg="yellow", font=("Calibri", 15), anchor="nw", justify="left", bd=4)
contact_label.place(relheight=0.9, relwidth=1)

contact_button = tk.Button(contacts_area, text="Add new contacts", bg="grey", fg="black", font=("Calibri", 10), justify="center", command=lambda: add_contacts())
contact_button.place(relx=0, rely=0.9,relheight=0.1, relwidth=1)


populate_name()
populate_mood()
populate_messages()
populate_contacts()


root.mainloop() # Used to end the area
