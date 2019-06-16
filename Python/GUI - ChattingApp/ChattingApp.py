import tkinter as tk
from tkinter import font
import requests
import os
import time
import datetime
import csv

# Changeable parameters - the dimensions of main window
HEIGHT = 600
WIDTH = 700

TITLE = "Chatting App"

# Filling the list of contacts
def populate_name(name):
    name_label['text'] = name

# Filling the list of contacts
def populate_mood(mood):
    mood_label['text'] = mood

# Filling the list of contacts
def populate_contacts():
    user_name = name_label['text']
    contact_label['text'] = ""
    # contacts = ["Georgina", "Maty", "Paul"]
    contacts = []
    with open('conversations.csv', 'r') as conversations_file:
        csv_reader = csv.DictReader(conversations_file, delimiter=";")
        # Looping through the conversation and seeing which users are in the
        #   same conversation as our user_name
        for entry in csv_reader:
            if entry['user_1'] == user_name:
                contacts.append(entry['user_2'])
            elif entry['user_2'] == user_name:
                contacts.append(entry['user_1'])

    # Putting all the contacts in the visible field
    for contact in contacts:
        contact_label['text'] += contact + "\n"

# Reading the content of a file and filling the appropriate text field
def populate_messages(conversation_id):
    print("populate messages")
    # # Reading from the helper txt file
    # with open('messages.txt', 'r') as file:
    #     content = file.read()
    #     messaging_label["state"] = "normal" # enabling to manipulate its content
    #     messaging_label.delete("1.0", "end") # deleting the old content
    #     messaging_label.insert("insert", content) # adding the new content
    #     messaging_label["state"] = "disabled" # disabling the content for user manipulation
    #     messaging_label.yview_moveto(1) # scrolling the scrollbar to the very bottom

    text_messages = ""

    with open('messages.csv', 'r') as messages_file:
        csv_reader = csv.DictReader(messages_file, delimiter=";")
        # Looping through the conversation and seeing which users are in the
        #   same conversation as our user_name
        for entry in csv_reader:
            print("entry:")
            print(entry)
            if entry['conversation_id'] == str(conversation_id):
                text_messages += "{}: {}\n".format(entry["user_name"], entry["message"])


    print("text messages", text_messages)

    messaging_label["state"] = "normal" # enabling to manipulate its content
    messaging_label.delete("1.0", "end") # deleting the old content
    messaging_label.insert("insert", text_messages) # adding the new content
    messaging_label["state"] = "disabled" # disabling the content for user manipulation


# Sending a message - saving it to the text file
def send_message(message):
    conversation_id = 1
    user_name = name_label["text"]
    current_timestamp = int(time.time())
    human_readable_time = datetime.datetime.fromtimestamp(current_timestamp).strftime('%Y-%m-%d %H:%M:%S')

    # # Reading the helper txt file
    # try:
    #     # Appending the file with "a+" mode
    #     with open('messages.txt', 'a+') as file:
    #         file.write("{}: {}\n".format(user_name, message))
    # except Excetion as e:
    #     print(e)
    #     return

    with open('messages.csv', 'a') as messages_file:
        csv_writer = csv.writer(messages_file, delimiter=";")

        input = []
        input.append(conversation_id)
        input.append(current_timestamp)
        input.append(user_name)
        input.append(message)

        csv_writer.writerow(input)

    messaging_text.delete("1.0", "end")
    populate_messages(conversation_id)

def show_settings():
    print("show settings")

def edit_mood():
    global edit_mood_window
    edit_mood_window = tk.Toplevel(main_window)
    edit_mood_window.title("Edit mood")
    edit_mood_window.geometry("400x200")

    mood_label = tk.Label(edit_mood_window, text="Please enter the new mood:", bg="yellow", font=("Calibri", 15), anchor="nw", justify="left", bd=4)
    mood_label.place(relheight=0.2, relwidth=1)

    mood_entry = tk.Entry(edit_mood_window, bg="orange", font=("Calibri", 15), bd=5)
    mood_entry.place(relx=0, rely=0.2, relheight=0.2, relwidth=0.7)

    mood_saving_button = tk.Button(edit_mood_window, text="Save new mood", bg="grey", fg="black", font=("Calibri", 10), justify="right", command=lambda: save_new_mood(mood_entry.get()))
    mood_saving_button.place(relx=0.2, rely=0.8, relheight=0.15, relwidth=0.25)

    mood_cancelling_button = tk.Button(edit_mood_window, text="Cancel", bg="grey", fg="black", font=("Calibri", 10), justify="right", command=lambda: close_window(edit_mood_window))
    mood_cancelling_button.place(relx=0.5, rely=0.8, relheight=0.15, relwidth=0.25)

def save_new_mood(mood):
    populate_mood(mood)
    close_window(edit_mood_window)

def close_window(window_name):
    window_name.destroy() # closing the specified window

def add_contacts():
    print("add_contacts")

# Defining the main window and its title
main_window = tk.Tk()
main_window.title(TITLE)

# Getting the initial screen-size
canvas = tk.Canvas(main_window, height=HEIGHT, width=WIDTH)
canvas.pack()

# Setting the background image - if the image exists in the current dir
# Having an if-statement not to be dependant on it in the case of .exe file
if os.path.isfile('./background.png'):
    background_image = tk.PhotoImage(file="background.png")
    background_label = tk.Label(main_window, image=background_image)
    background_label.place(x=0, y=0, relwidth=1, relheight=1)


# PROFILE PART
profile_area = tk.Frame(main_window, bg="#42b6f4", bd=5)
profile_area.place(relx=0.05, rely=0.1, relwidth=0.45, relheight=0.15)

name_label = tk.Label(profile_area, bg="yellow", font=("Calibri", 15), anchor="nw", justify="left", bd=4)
name_label.place(rely=0, relheight=0.5, relwidth=0.75)

mood_label = tk.Label(profile_area, bg="yellow", font=("Calibri", 15), anchor="nw", justify="left", bd=4)
mood_label.place(rely=0.5, relheight=0.5, relwidth=0.75)

settings_button = tk.Button(profile_area, text="Settings", bg="grey", fg="black", font=("Calibri", 10), justify="right", command=lambda: show_settings())
settings_button.place(relx=0.75, rely=0, relheight=0.5, relwidth=0.25)

mood_button = tk.Button(profile_area, text="Edit mood", bg="grey", fg="black", font=("Calibri", 10), justify="right", command=lambda: edit_mood())
mood_button.place(relx=0.75, rely=0.5, relheight=0.5, relwidth=0.25)


# MESSAGING PART
messaging_area = tk.Frame(main_window, bg="#42b6f4", bd=10)
messaging_area.place(relx=0.3, rely=0.3, relwidth=0.65, relheight=0.6)

scrollbar = tk.Scrollbar(messaging_area)
scrollbar.place(relx=0.95, relheight=0.8, relwidth=0.05)

messaging_label = tk.Text(messaging_area, bg="yellow", font=("Calibri", 15), state="disabled", bd=4, yscrollcommand=scrollbar.set)
messaging_label.place(relheight=0.8, relwidth=0.95)

scrollbar.config( command = messaging_label.yview )

messaging_text = tk.Text(messaging_area, bg="orange", font=("Calibri", 15), bd=5)
messaging_text.place(relx=0, rely=0.8, relheight=0.2, relwidth=0.8)

messaging_button = tk.Button(messaging_area, text="Send", bg="grey", fg="black", font=("Calibri", 10), justify="center", command=lambda: send_message(messaging_text.get("1.0", "end-1c")))
messaging_button.place(relx=0.8, rely=0.8,relheight=0.2, relwidth=0.2)


# CONTACTS PART
contacts_area = tk.Frame(main_window, bg="#42b6f4", bd=10)
contacts_area.place(relx=0.05, rely=0.3, relwidth=0.2, relheight=0.6)

contact_label = tk.Label(contacts_area, text="contacts", bg="yellow", font=("Calibri", 15), anchor="nw", justify="left", bd=4)
contact_label.place(relheight=0.9, relwidth=1)

contact_button = tk.Button(contacts_area, text="Add new contacts", bg="grey", fg="black", font=("Calibri", 10), justify="center", command=lambda: add_contacts())
contact_button.place(relx=0, rely=0.9,relheight=0.1, relwidth=1)


# Populating all the fields in the beginning
populate_name("George")
populate_mood("I am in a good mood")
populate_messages(1)
populate_contacts()


main_window.mainloop()
