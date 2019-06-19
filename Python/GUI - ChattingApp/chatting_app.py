import tkinter as tk
from tkinter import font
import requests
import os
import time
import datetime
import csv
import pandas as pd

TITLE = "Chatting App"

# Username will be stored globally, to be accessible easily everywhere
# Will get initialised right after user authenticates
USERNAME = ""

# Filling the name
def populate_name(name):
    if name == False:
        name_label['text'] = ""
        return

    global USERNAME
    USERNAME = name
    name_label['text'] = name

def load_mood(user_name, known_mood=""):
    # If the mood is already known (user has just edited it), it will be supplied as a parameter
    if known_mood != "":
        mood_label['text'] = known_mood
        return

    with open('users.csv', 'r') as users_file:
        csv_reader = csv.DictReader(users_file)
        # Looping through the conversation and seeing which users are in the
        #   same conversation as our user_name
        for entry in csv_reader:
            print("entry - user", entry)
            if entry['name'] == user_name:
                mood_label['text'] = entry['mood']
                break

# Filling the mood
def populate_mood(mood):
    mood_label['text'] = mood

# Filling the list of contacts, each as a button
def populate_contacts():
    user_name = USERNAME
    contacts = []
    with open('conversations.csv', 'r') as conversations_file:
        csv_reader = csv.DictReader(conversations_file)
        # Looping through the conversation and seeing which users are in the
        #   same conversation as our user_name
        for entry in csv_reader:
            if entry['user_1'] == user_name:
                contacts.append({
                    "name": entry['user_2'],
                    "conv_id": entry['id']
                })
            elif entry['user_2'] == user_name:
                contacts.append({
                    "name": entry['user_1'],
                    "conv_id": entry['id']
                })

    # Deleting all the previous buttons with contacts if they exist
    for button in contact_space_for_buttons.winfo_children():
        button.destroy()

    # Creating new buttons with the corresponding label for each contact
    for index, user in enumerate(contacts):
        print("index", index)

        name = user["name"]
        conversation_id = user["conv_id"]
        print("name", name)
        print("conv_id", conversation_id)
        button = tk.Button(contact_space_for_buttons, text=name, bg="grey", fg="black", font=("Calibri", 10), justify="center", command=lambda conversation_id = conversation_id, index=index, name=name: populate_messages(conversation_id, name))
        button.place(relx=0, rely=(0.11 * index),relheight=0.1, relwidth=1)

# Reading the content of a file and filling the appropriate text field
def populate_messages(conversation_id, name):
    if conversation_id == False:
        messaging_label["state"] = "normal" # enabling to manipulate its content
        messaging_label.delete("1.0", "end") # deleting the old content
        messaging_label["state"] = "disabled" # disabling the content for user manipulation
        return

    text_messages = ""

    with open('messages.csv', 'r') as messages_file:
        csv_reader = csv.DictReader(messages_file)
        # Looping through the conversation and seeing which users are in the
        #   same conversation as our user_name
        for entry in csv_reader:
            if entry['conversation_id'] == str(conversation_id):
                text_messages += "{}: {}\n".format(entry["user_name"], entry["message"])

    messaging_label["state"] = "normal" # enabling to manipulate its content
    messaging_label.delete("1.0", "end") # deleting the old content
    messaging_label.insert("insert", text_messages) # adding the new content
    messaging_label["state"] = "disabled" # disabling the content for user manipulation
    messaging_label.yview_moveto(1) # scrolling the scrollbar to the very bottom

    current_contact_label["text"] = "Current contact - {}".format(name)


# Sending a message - saving it to the text file
def send_message(message, conversation_id):
    user_name = USERNAME
    current_timestamp = int(time.time())
    human_readable_time = datetime.datetime.fromtimestamp(current_timestamp).strftime('%Y-%m-%d %H:%M:%S')

    # Appending the new message to a CSV file
    with open('messages.csv', 'a') as messages_file:
        csv_writer = csv.writer(messages_file)

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
    print("settings")
    global settings_window
    settings_window = tk.Toplevel(main_window)
    settings_window.title("Add settings")
    settings_window.geometry("400x200")

    settings_label = tk.Label(settings_window, text="Choose your settings:", bg="yellow", font=("Calibri", 15), anchor="nw", justify="left", bd=4)
    settings_label.place(relheight=0.2, relwidth=1)

    settings_entry = tk.Entry(settings_window, bg="orange", font=("Calibri", 15), bd=5)
    settings_entry.place(relx=0, rely=0.2, relheight=0.2, relwidth=0.7)

    settings_saving_button = tk.Button(settings_window, text="Save new settings", bg="grey", fg="black", font=("Calibri", 10), justify="right", command=lambda: save_new_settings(settings_entry.get()))
    settings_saving_button.place(relx=0.2, rely=0.8, relheight=0.15, relwidth=0.25)

    settings_cancelling_button = tk.Button(settings_window, text="Cancel", bg="grey", fg="black", font=("Calibri", 10), justify="right", command=lambda: close_window(edit_settings_window))
    settings_cancelling_button.place(relx=0.5, rely=0.8, relheight=0.15, relwidth=0.25)

def close_window(window_name):
    window_name.destroy() # closing the specified window

def send_contact_request(name):
    print(name)

def add_contacts():
    print("add_contacts")
    global add_contacts_window
    add_contacts_window = tk.Toplevel(main_window)
    add_contacts_window.title("Add contacts")
    add_contacts_window.geometry("600x400")

    add_contacts_label = tk.Label(add_contacts_window, text="Type the friend's name:", bg="yellow", bd=4)
    add_contacts_label.place(relx=0, rely=0, relheight=0.1, relwidth=1)

    contacts_entry = tk.Entry(add_contacts_window, bg="orange", font=("Calibri", 15), bd=5)
    contacts_entry.place(relx=0, rely=0.1, relheight=0.2, relwidth=0.7)


    add_contacts_space_for_buttons = tk.Text(add_contacts_window, bg="yellow", bd=4)
    add_contacts_space_for_buttons.place(relx=0, rely=0.3, relheight=0.7, relwidth=1)

    info_label = tk.Label(add_contacts_window, text="Click a name to add to contacts:", bg="yellow", bd=4)
    info_label.place(relx=0, rely=0.9, relheight=0.1, relwidth=1)

    list_of_all_users = []

    # Filling the list of all other users apart from the current one
    with open('users.csv', 'r') as users_file:
        csv_reader = csv.DictReader(users_file)
        for entry in csv_reader:
            if entry["name"] != USERNAME:
                list_of_all_users.append(entry["name"])

    print("list of all users", list_of_all_users)

    # Creating new buttons with the corresponding label for each contact
    for index, user in enumerate(list_of_all_users):
        button = tk.Button(add_contacts_space_for_buttons, text=user, bg="grey", fg="black", font=("Calibri", 10), justify="center", command=lambda user=user: send_contact_request(user))
        button.place(relx=0, rely=(0.11 * index),relheight=0.1, relwidth=1)

def manage_contact_requests():
    print("manage_contact_requests")
    global manage_contacts_window
    manage_contacts_window = tk.Toplevel(main_window)
    manage_contacts_window.title("Manage contacts requests")
    manage_contacts_window.geometry("600x600")

    manage_contacts_space_for_buttons = tk.Text(manage_contacts_window, bg="yellow", bd=4)
    manage_contacts_space_for_buttons.place(relx=0, rely=0.1, relheight=0.65, relwidth=1)

    contacts_saving_button = tk.Button(manage_contacts_window, text="Save new contacts", bg="grey", fg="black", font=("Calibri", 10), justify="right", command=lambda: save_new_contacts(contacts_entry.get()))
    contacts_saving_button.place(relx=0.2, rely=0.8, relheight=0.15, relwidth=0.25)

    contacts_cancelling_button = tk.Button(manage_contacts_window, text="Cancel", bg="grey", fg="black", font=("Calibri", 10), justify="right", command=lambda: close_window(edit_contacts_window))
    contacts_cancelling_button.place(relx=0.5, rely=0.8, relheight=0.15, relwidth=0.25)

    list_of_users_requesting_contact = []

    # Filling the list of all other users apart from the current one
    with open('contact_requests.csv', 'r') as contact_requests_file:
        csv_reader = csv.DictReader(contact_requests_file)
        for entry in csv_reader:
            if entry["other_user"] == USERNAME:
                list_of_users_requesting_contact.append(entry["sender_user"])

    print("list_of_users_requesting_contact", list_of_users_requesting_contact)

    # Creating new buttons with the corresponding label for each contact
    for index, user in enumerate(list_of_users_requesting_contact):
        button = tk.Button(manage_contacts_space_for_buttons, text=user, bg="grey", fg="black", font=("Calibri", 10), justify="center", command=lambda user=user: send_contact_request(user))
        button.place(relx=0, rely=(0.1 * index),relheight=0.1, relwidth=1)

# Defining the main window and its title
main_window = tk.Tk()
main_window.state('zoomed') # Making the window maximized
main_window.title(TITLE)

def handle_closing_login_windows(result, user_name):
    # close_window(login_result_window)
    if result == "SUCCESS":
        # close_window(login_window)

        # Populating all the fields in the beginning
        populate_name(user_name)
        load_mood(user_name)
        # populate_messages(1)
        messaging_label["state"] = "normal" # enabling to manipulate its content
        messaging_label.delete("1.0", "end")
        messaging_label.insert("insert", "Please choose a contact to start a conversation!")
        messaging_label["state"] = "disabled" # disabling the content for user manipulation

        populate_contacts()
    else:
        reset_login()

def show_result_from_login(result, user_name):
    global login_result_window
    login_result_window = tk.Toplevel(login_window)
    login_result_window.title("Login result")
    login_result_window.geometry("400x200")

    text = ""

    if result == "SUCCESS":
        text = "Login successful, welcome!"
    else:
        text = "Login failed, please try again!"

    login_result_label = tk.Label(login_result_window, text=text, bg="yellow", font=("Calibri", 15), anchor="nw", justify="left", bd=4)
    login_result_label.place(relx=0.1, rely=0.1, relheight=0.5, relwidth=0.8)

    login_result_button = tk.Button(login_result_window, text="Close", bg="yellow", font=("Calibri", 15), anchor="nw", justify="left", bd=4, command=lambda: handle_closing_login_windows(result, user_name))
    login_result_button.place(relx=0.4, rely=0.75, relheight=0.2, relwidth=0.2)


def login_into_application():
    user_name = login_username_entry.get()
    password = login_password_entry.get()

    message=""

    print("username", user_name)
    print("password", password)

    with open('users.csv', 'r') as users_file:
        user_list = csv.DictReader(users_file)
        # Looping through the conversation and seeing which users are in the
        #   same conversation as our user_name
        for user in user_list:
            print("entry - user", user)
            if user['name'] == user_name:
                if user['password'] == password:
                    message = "SUCCESS"
                else:
                    message = "FAILURE"
                break

    print(message)
    show_result_from_login(message, user_name)


def reset_login():
    login_username_entry.delete(0, "end")
    login_password_entry.delete(0, "end")

def login_screen():
    global login_window
    login_window = tk.Toplevel(main_window)
    login_window.title("Login")
    login_window.geometry("500x300")

    login_label = tk.Label(login_window, text="Please enter you login details:", bg="yellow", font=("Calibri", 15), anchor="nw", justify="left", bd=4)
    login_label.place(relheight=0.2, relwidth=1)

    login_username_label = tk.Label(login_window, text="Username:", bg="yellow", font=("Calibri", 15), anchor="nw", justify="left", bd=4)
    login_username_label.place(relx=0.05, rely=0.2, relheight=0.2, relwidth=0.3)

    global login_username_entry
    login_username_entry = tk.Entry(login_window, bg="orange", font=("Calibri", 15), bd=5)
    login_username_entry.place(relx=0.4, rely=0.2, relheight=0.2, relwidth=0.55)

    login_password_label = tk.Label(login_window, text="Password:", bg="yellow", font=("Calibri", 15), anchor="nw", justify="left", bd=4)
    login_password_label.place(relx=0.05, rely=0.5, relheight=0.2, relwidth=0.3)

    global login_password_entry
    login_password_entry = tk.Entry(login_window, bg="orange", font=("Calibri", 15), bd=5, show="*")
    login_password_entry.place(relx=0.4, rely=0.5, relheight=0.2, relwidth=0.55)

    login_button_login = tk.Button(login_window, text="Login", bg="grey", fg="black", font=("Calibri", 10), justify="right", command=lambda: login_into_application())
    login_button_login.place(relx=0.1, rely=0.8, relheight=0.15, relwidth=0.25)

    login_button_reset = tk.Button(login_window, text="Reset", bg="grey", fg="black", font=("Calibri", 10), justify="right", command=lambda: reset_login())
    login_button_reset.place(relx=0.4, rely=0.8, relheight=0.15, relwidth=0.25)

    login_button_register = tk.Button(login_window, text="Register", bg="grey", fg="black", font=("Calibri", 10), justify="right", command=lambda: register_screen())
    login_button_register.place(relx=0.7, rely=0.8, relheight=0.15, relwidth=0.25)

def handle_closing_register_windows(result):
    close_window(register_result_window)
    if result == "SUCCESS":
        close_window(register_window)
    else:
        reset_register()

def show_result_from_register(result):
    global register_result_window
    register_result_window = tk.Toplevel(login_window)
    register_result_window.title("Login result")
    register_result_window.geometry("400x200")

    text = ""

    if result == "SUCCESS":
        text = "Registration successful, welcome!"
    else:
        text = "Login failed, please try again!"

    login_result_label = tk.Label(register_result_window, text=text, bg="yellow", font=("Calibri", 15), anchor="nw", justify="left", bd=4)
    login_result_label.place(relx=0.1, rely=0.1, relheight=0.5, relwidth=0.8)

    login_result_button = tk.Button(register_result_window, text="Close", bg="yellow", font=("Calibri", 15), anchor="nw", justify="left", bd=4, command=lambda: handle_closing_register_windows(result))
    login_result_button.place(relx=0.4, rely=0.75, relheight=0.2, relwidth=0.2)

def register_into_application():
    user_name = register_username_entry.get()
    password = register_password_entry.get()
    password_verify = register_password_entry_verify.get()

    # Checking if the password was typed both times the same
    if (password != password_verify):
        print("NOT THE SAME PASSWORD")
        show_result_from_register("NOT SAME PASSWORD")
        return

    # Checking if there is not already a user with the same name
    with open('users.csv', 'r') as users_file:
        user_list = csv.DictReader(users_file)
        # Looping through the users and looking for the same username
        for user in user_list:
            if user['name'] == user_name:
                message = "USER ALREADY EXISTS"
                show_result_from_register(message)
                return

    # Appending the new user to a CSV file (if relevant)
    with open('users.csv', 'a') as users_file:
        csv_writer = csv.writer(users_file)

        input = []
        input.append(user_name)
        input.append("new mood")
        input.append("new gender")
        input.append(123465)
        input.append(123465)
        input.append(password)

        csv_writer.writerow(input)

    show_result_from_register("SUCCESS")

def reset_register():
    register_username_entry.delete(0, "end")
    register_password_entry.delete(0, "end")
    register_password_entry_verify.delete(0, "end")

def register_screen():
    global register_window
    register_window = tk.Toplevel(main_window)
    register_window.title("Login")
    register_window.geometry("500x300")

    register_label = tk.Label(register_window, text="Please enter you details:", bg="yellow", font=("Calibri", 15), anchor="nw", justify="left", bd=4)
    register_label.place(relheight=0.2, relwidth=1)

    register_username_label = tk.Label(register_window, text="Username:", bg="yellow", font=("Calibri", 15), anchor="nw", justify="left", bd=4)
    register_username_label.place(relx=0.05, rely=0.15, relheight=0.15, relwidth=0.3)

    global register_username_entry
    register_username_entry = tk.Entry(register_window, bg="orange", font=("Calibri", 15), bd=5)
    register_username_entry.place(relx=0.4, rely=0.15, relheight=0.15, relwidth=0.55)

    register_password_label = tk.Label(register_window, text="Password:", bg="yellow", font=("Calibri", 15), anchor="nw", justify="left", bd=4)
    register_password_label.place(relx=0.05, rely=0.35, relheight=0.15, relwidth=0.3)

    global register_password_entry
    register_password_entry = tk.Entry(register_window, bg="orange", font=("Calibri", 15), bd=5, show="*")
    register_password_entry.place(relx=0.4, rely=0.35, relheight=0.15, relwidth=0.55)

    register_password_label_verify = tk.Label(register_window, text="Password again:", bg="yellow", font=("Calibri", 15), anchor="nw", justify="left", bd=4)
    register_password_label_verify.place(relx=0.05, rely=0.55, relheight=0.15, relwidth=0.3)

    global register_password_entry_verify
    register_password_entry_verify = tk.Entry(register_window, bg="orange", font=("Calibri", 15), bd=5, show="*")
    register_password_entry_verify.place(relx=0.4, rely=0.55, relheight=0.15, relwidth=0.55)

    register_button_reset = tk.Button(register_window, text="Reset", bg="grey", fg="black", font=("Calibri", 10), justify="right", command=lambda: reset_register())
    register_button_reset.place(relx=0.4, rely=0.8, relheight=0.15, relwidth=0.25)

    register_button_register = tk.Button(register_window, text="Register", bg="grey", fg="black", font=("Calibri", 10), justify="right", command=lambda: register_into_application())
    register_button_register.place(relx=0.7, rely=0.8, relheight=0.15, relwidth=0.25)

def edit_mood(main_window):
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

# Changes the mood in the DB (CSV file)
def save_new_mood(mood):
    user_name = USERNAME

    users_file = pd.read_csv("users.csv")
    users_file.loc[users_file["name"]==user_name, "mood"] = mood
    users_file.to_csv("users.csv", index=False)

    # Showing the change to the user and closing the editing window
    load_mood(user_name, mood)
    close_window(edit_mood_window)

def log_out_from_application():
    global USERNAME
    USERNAME=""
    print("logging off")

    name_label["text"] = ""
    mood_label["text"] = ""

    messaging_label["state"] = "normal" # enabling to manipulate its content
    messaging_label.delete("1.0", "end")
    messaging_label["state"] = "disabled" # disabling the content for user manipulation

    # populate_name(False)
    # populate_mood(False)
    # populate_contacts(False)
    # populate_messages(False)

    # for slave in contact_space_for_buttons.pack_slaves():
    #     print(slave["text"])

    # Deleting all the buttons with contacts
    for widget in contact_space_for_buttons.winfo_children():
        print(widget["text"])
        widget.destroy()


# Getting the initial screen-size
canvas = tk.Canvas(main_window)
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

mood_button = tk.Button(profile_area, text="Edit mood", bg="grey", fg="black", font=("Calibri", 10), justify="right", command=lambda: edit_mood(main_window))
mood_button.place(relx=0.75, rely=0.5, relheight=0.5, relwidth=0.25)


# LOGIN/LOGOFF PART
login_area = tk.Frame(main_window, bg="yellow", bd=5)
login_area.place(relx=0.7, rely=0.05, relwidth=0.25, relheight=0.15)

login_button = tk.Button(login_area, text="LOGIN", bg="green", fg="black", font=("Calibri", 10), justify="right", command=lambda: login_screen())
login_button.place(relx=0.1, rely=0.1, relheight=0.5, relwidth=0.4)

logout_button = tk.Button(login_area, text="LOGOUT", bg="red", fg="black", font=("Calibri", 10), justify="right", command=lambda: log_out_from_application())
logout_button.place(relx=0.55, rely=0.1, relheight=0.5, relwidth=0.4)


# MESSAGING PART
messaging_area = tk.Frame(main_window, bg="#42b6f4", bd=10)
messaging_area.place(relx=0.3, rely=0.3, relwidth=0.65, relheight=0.65)

current_contact_label = tk.Label(messaging_area, text="Current contact name - ", bg="yellow", font=("Calibri", 15), justify="left", bd=4)
current_contact_label.place(relx=0, rely=0, relheight=0.09, relwidth=0.97)

scrollbar = tk.Scrollbar(messaging_area)
scrollbar.place(relx=0.97, relheight=0.8, relwidth=0.05)

messaging_label = tk.Text(messaging_area, bg="yellow", font=("Calibri", 15), state="disabled", bd=4, yscrollcommand=scrollbar.set)
messaging_label.place(relx=0, rely=0.1, relheight=0.8, relwidth=0.97)

scrollbar.config(command=messaging_label.yview)

messaging_text = tk.Text(messaging_area, bg="orange", font=("Calibri", 15), bd=5)
messaging_text.place(relx=0, rely=0.8, relheight=0.2, relwidth=0.8)

messaging_button = tk.Button(messaging_area, text="Send", bg="grey", fg="black", font=("Calibri", 10), justify="center", command=lambda: send_message(messaging_text.get("1.0", "end-1c"), 1))
messaging_button.place(relx=0.8, rely=0.8,relheight=0.2, relwidth=0.2)


# CONTACTS PART
contacts_area = tk.Frame(main_window, bg="#42b6f4", bd=10)
contacts_area.place(relx=0.05, rely=0.3, relwidth=0.2, relheight=0.65)

# contact_space_for_buttons = tk.Label(contacts_area, bg="yellow", font=("Calibri", 15), anchor="nw", justify="left", bd=4)
contact_space_for_buttons = tk.Text(contacts_area, bg="yellow", font=("Calibri", 15), bd=4)
contact_space_for_buttons.place(relheight=0.9, relwidth=1)

# names = [{"name": "George", "conv_id": 14}, {"name": "Michael", "conv_id": 16}, {"name": "John", "conv_id": 1}, {"name": "Rachel", "conv_id": 11}, {"name": "Lorcan", "conv_id": 15}]
#
# for index, user in enumerate(names):
#     print("index", index)
#
#     name = user["name"]
#     conversation_id = user["conv_id"]
#     print("name", name)
#     print("conv_id", conversation_id)
#     button = tk.Button(contact_space_for_buttons, text=name, bg="grey", fg="black", font=("Calibri", 10), justify="center", command=lambda conversation_id = conversation_id, index=index, name=name: populate_messages(conversation_id))
#     button.place(relx=0, rely=(0.11 * index),relheight=0.1, relwidth=1)

# contact_name_1 = tk.Button(contact_space_for_buttons, text="George", bg="grey", fg="black", font=("Calibri", 10), justify="center", command=lambda: add_contacts())
# contact_name_1.place(relx=0, rely=0.0,relheight=0.1, relwidth=1)
#
# contact_name_2 = tk.Button(contact_space_for_buttons, text="Michael", bg="grey", fg="black", font=("Calibri", 10), justify="center", command=lambda: add_contacts())
# contact_name_2.place(relx=0, rely=0.11,relheight=0.1, relwidth=1)


contact_new_button = tk.Button(contacts_area, text="Add new contacts", bg="grey", fg="black", font=("Calibri", 10), justify="center", command=lambda: add_contacts())
contact_new_button.place(relx=0, rely=0.8,relheight=0.1, relwidth=1)

contact_requests_button = tk.Button(contacts_area, text="Manage requests (0)", bg="grey", fg="black", font=("Calibri", 10), justify="center", command=lambda: manage_contact_requests())
contact_requests_button.place(relx=0, rely=0.9,relheight=0.1, relwidth=1)

# Saving time with no login :)
# WARNING: need to uncomment the commented closing of windows
handle_closing_login_windows("SUCCESS", "George")

main_window.mainloop()
