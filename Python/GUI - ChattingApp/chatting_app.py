import tkinter as tk
from tkinter import font
import os
import time
import datetime
import csv
import pandas as pd
import sched

TITLE = "Chatting App"

# USER_NAME will be stored globally, to be accessible easily everywhere
# Will get initialised right after user authenticates
USER_NAME = ""

CURRENTLY_OPENED_CONTACT_NAME = ""

CURRENT_CONVERSATION_ID = ""

# Filling the name
def populate_name(name):
    if name == False:
        name_label['text'] = ""
        return

    global USER_NAME
    USER_NAME = name
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
    user_name = USER_NAME
    contacts = []
    with open('conversations.csv', 'r') as conversations_file:
        csv_reader = csv.DictReader(conversations_file)
        # Looping through the conversation and seeing which users are in the
        #   same conversation as our user_name (searching for their contacts)
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

    # Getting array of all names (for the search in users table)
    all_contact_names = []
    for contact in contacts:
        all_contact_names.append(contact["name"])

    # Including the timestamps for all contacts
    with open('users.csv', 'r') as users_file:
        csv_reader = csv.DictReader(users_file)
        # Looping through the users and seeing whether they are in current user's
        #   contacts, and if so, saving their last time online timestamp
        for entry in csv_reader:
            if entry['name'] in all_contact_names:
                for index, contact in enumerate(contacts):
                    if contact["name"] == entry['name']:
                        contacts[index]["last_time_online"] = int(entry["last_time_online"])

    print("contacts: ", contacts)

    # Deleting all the previous buttons with contacts if they exist
    for button in contact_space_for_buttons.winfo_children():
        button.destroy()

    # Creating new buttons with the corresponding label for each contact
    for index, user in enumerate(contacts):
        print("index", index)

        user_name = user["name"]
        conversation_id = user["conv_id"]
        last_timestamp = user["last_time_online"]
        print("user_name", user_name)
        print("conv_id", conversation_id)

        current_timestamp = int(time.time())
        print("current_timestamp", current_timestamp)

        # Determining how long time passed from the user being online the last time
        time_from_last_online_state = current_timestamp - last_timestamp

        label_background_color = ""

        # Setting label's colour according to the last online date
        if time_from_last_online_state < 60:
            label_background_color = "green"
        elif time_from_last_online_state < 300:
            label_background_color = "orange"
        else:
            label_background_color = "red"

        # Label that is visually showing whether the user is online or not
        online_status_label = tk.Button(contact_space_for_buttons, bg=label_background_color)
        online_status_label.place(relx=0, rely=(0.11 * index),relheight=0.1, relwidth=0.2)

        button_with_contact_user_name = tk.Button(contact_space_for_buttons, text=user_name, bg="grey", fg="black", font=("Calibri", 10), justify="center", command=lambda conversation_id = conversation_id, user_name=user_name: populate_messages(conversation_id, user_name))
        button_with_contact_user_name.place(relx=0.25, rely=(0.11 * index),relheight=0.1, relwidth=0.5)

        info_button = tk.Button(contact_space_for_buttons, text="INFO", bg="grey", fg="black", font=("Calibri", 10), justify="center", command=lambda user_name=user_name: show_user_info(user_name))
        info_button.place(relx=0.8, rely=(0.11 * index),relheight=0.1, relwidth=0.2)

def show_user_info(user_name):
    print("show user info", user_name)
    global show_user_info_window
    show_user_info_window = tk.Toplevel(main_window)
    show_user_info_window.title("User info")
    show_user_info_window.geometry("600x400")

    label_text = "{}'s information:".format(user_name)

    user_mood = ""
    last_time_online = 0

    # Searching for the information about a specific user
    with open('users.csv', 'r') as users_file:
        csv_reader = csv.DictReader(users_file)
        # Looping through the users and seeing whether they are in current user's
        #   contacts, and if so, saving their last time online timestamp
        for entry in csv_reader:
            if entry["name"] == user_name:
                user_mood = entry["mood"]
                last_time_online = int(entry["last_time_online"])
                break

    human_readable_last_time_online = datetime.datetime.fromtimestamp(last_time_online).strftime('%Y-%m-%d %H:%M:%S')

    mood_label_text = "Mood: {}".format(user_mood)
    last_time_online_text = "Last time online: {}".format(human_readable_last_time_online)

    show_user_info_label = tk.Label(show_user_info_window, text=label_text, bg="yellow", font=("Calibri", 15), anchor="nw", justify="left", bd=4)
    show_user_info_label.place(relx=0, rely=0, relheight=0.2, relwidth=1)

    mood_info_label = tk.Label(show_user_info_window, text=mood_label_text, bg="yellow", font=("Calibri", 15), anchor="nw", justify="left", bd=4)
    mood_info_label.place(relx=0, rely=0.2, relheight=0.2, relwidth=1)

    timestamp_info_label = tk.Label(show_user_info_window, text=last_time_online_text, bg="yellow", font=("Calibri", 15), anchor="nw", justify="left", bd=4)
    timestamp_info_label.place(relx=0, rely=0.4, relheight=0.2, relwidth=1)

    show_user_info_cancelling_button = tk.Button(show_user_info_window, text="Cancel", bg="grey", fg="black", font=("Calibri", 10), justify="right", command=lambda: close_window(show_user_info_window))
    show_user_info_cancelling_button.place(relx=0.8, rely=0.9, relheight=0.1, relwidth=0.2)

# Reading the content of a file and filling the appropriate text field
def populate_messages(conversation_id, user_name):
    global CURRENT_CONVERSATION_ID
    global CURRENTLY_OPENED_CONTACT_NAME
    CURRENT_CONVERSATION_ID = conversation_id
    CURRENTLY_OPENED_CONTACT_NAME = user_name

    text_messages = ""

    with open('messages.csv', 'r') as messages_file:
        csv_reader = csv.DictReader(messages_file)
        # Looping through the conversation and seeing which users are in the
        #   same conversation as our user_name
        for entry in csv_reader:
            if entry['conversation_id'] == str(conversation_id):
                text_messages += "{}: {}\n".format(entry["user_name"], entry["message"])

    # If there are no messages yet, display the initial message to break the silence :)
    if text_messages == "":
        text_messages = "Greet your new contact {}!".format(user_name)

    messaging_label["state"] = "normal" # enabling to manipulate its content
    messaging_label.delete("1.0", "end") # deleting the old content
    messaging_label.insert("insert", text_messages) # adding the new content
    messaging_label["state"] = "disabled" # disabling the content for user manipulation
    messaging_label.yview_moveto(1) # scrolling the scrollbar to the very bottom

    current_contact_label["text"] = "Current contact - {}".format(user_name)


# Sending a message - saving it to the text file
# Also updating the conversation table and storing the time of message as a last timestamp
def send_message(message, conversation_id):
    user_name = USER_NAME
    current_timestamp = int(time.time())
    human_readable_time = datetime.datetime.fromtimestamp(current_timestamp).strftime('%Y-%m-%d %H:%M:%S')

    # Appending the new message to a CSV file
    with open('messages.csv', 'a') as messages_file:
        csv_writer = csv.writer(messages_file)

        message_row = []
        message_row.append(conversation_id)
        message_row.append(current_timestamp)
        message_row.append(user_name)
        message_row.append(message)

        csv_writer.writerow(message_row)

    # Deleting the entry field
    messaging_text.delete("1.0", "end")

    current_timestamp = int(time.time())

    conversations_file = pd.read_csv("conversations.csv")
    conversations_file.loc[conversations_file["id"]==conversation_id, "last_timestamp"] = current_timestamp
    conversations_file.to_csv("conversations.csv", index=False)

    # Populating the message label with a new content
    # TODO: do not refresh everything, just add a new line, and store it locally
    populate_messages(CURRENT_CONVERSATION_ID, CURRENTLY_OPENED_CONTACT_NAME)

def save_new_settings():
    print("save new settings")

def show_settings():
    print("show settings")
    global settings_window
    settings_window = tk.Toplevel(main_window)
    settings_window.title("Add settings")
    settings_window.geometry("600x400")

    settings_label = tk.Label(settings_window, text="Choose your settings:", bg="yellow", font=("Calibri", 15), anchor="nw", justify="left", bd=4)
    settings_label.place(relheight=0.2, relwidth=1)

    settings_saving_button = tk.Button(settings_window, text="Save new settings", bg="grey", fg="black", font=("Calibri", 10), justify="right", command=lambda: save_new_settings())
    settings_saving_button.place(relx=0, rely=0.9, relheight=0.1, relwidth=0.2)

    contacts_cancelling_button = tk.Button(settings_window, text="Cancel", bg="grey", fg="black", font=("Calibri", 10), justify="right", command=lambda: close_window(settings_window))
    contacts_cancelling_button.place(relx=0.8, rely=0.9, relheight=0.1, relwidth=0.2)

def close_window(window_name):
    window_name.destroy() # closing the specified window

# Accepts the request to be added as a contact
# Removing the request from contact_requests and creating a new conversation in conversations
# After successful saving of everything, reload the contacts bar to show the new conversation
def accept_contact_request(name):
    print("Accepting request from:", name)
    # Making sure all the requests with those two names are deleted
    with open('contact_requests.csv', 'r') as contact_requests_file_read:
        csv_reader = list(csv.reader(contact_requests_file_read))

    with open('contact_requests.csv', 'w') as contact_requests_file_write:
        csv_writer = csv.writer(contact_requests_file_write)

        for row in csv_reader:
            if len(row) == 0:
                continue
            if not ((row[0] == name and row[1] == USER_NAME) or (row[0] == USER_NAME and row[1] == name)):
                csv_writer.writerow(row)

    # Finding out the index of last conversation, to increment it by one in the new conversation
    with open('conversations.csv', 'r') as conversations_file:
        csv_reader = list(csv.reader(conversations_file))
        highest_index = 0
        # The last line of CSV file can be empty, so in that case take the last but one
        try:
            highest_index = int(csv_reader[-1][0])
        except IndexError:
            highest_index = int(csv_reader[-2][0])

    # Creating a new entry in the conversation
    with open('conversations.csv', 'a') as conversations_file:
        csv_writer = csv.writer(conversations_file)

        conversation_row = []
        conversation_row.append(highest_index + 1)
        conversation_row.append(name)
        conversation_row.append(USER_NAME)
        conversation_row.append(15487654641)

        csv_writer.writerow(conversation_row)

    print("New conversation with index {} was created".format(highest_index + 1))
    # Updating the contact section to include the new contact
    populate_contacts()

# Sends request to some other user to be added as a contact
def send_contact_request(user_name):
    print("Contact request was sent to", user_name)
    with open('contact_requests.csv', 'a') as contact_requests_file:
        csv_writer = csv.writer(contact_requests_file)

        sender_user = USER_NAME
        other_user = user_name

        contact_request_row = []
        contact_request_row.append(sender_user)
        contact_request_row.append(other_user)

        csv_writer.writerow(contact_request_row)

# Accepts a new contact, updates the requests and closes the confirmation window
def add_new_contact_and_close_dialog(user_name):
    send_contact_request(user_name)
    close_window(add_new_contact_confirmation_window)

# Confirms whether user really wants to accept contact
def add_new_contact_confirmation(user_name):
    global add_new_contact_confirmation_window
    add_new_contact_confirmation_window = tk.Toplevel(main_window)
    add_new_contact_confirmation_window.title("Accept contact request?")
    add_new_contact_confirmation_window.geometry("500x200")

    text_in_the_label = "Do you really want to add user \"{}\" to the contacts?".format(user_name)

    accept_contact_confirmation_label = tk.Label(add_new_contact_confirmation_window, text=text_in_the_label, bg="yellow", font=("Calibri", 15), anchor="nw", justify="left", bd=4)
    accept_contact_confirmation_label.place(relx=0, rely=0, relheight=0.5, relwidth=1)

    accept_contact_confirmation_yes_button = tk.Button(add_new_contact_confirmation_window, text="Yes", bg="grey", fg="black", font=("Calibri", 10), justify="right", command=lambda: add_new_contact_and_close_dialog(user_name))
    accept_contact_confirmation_yes_button.place(relx=0.2, rely=0.6, relheight=0.4, relwidth=0.25)

    accept_contact_confirmation_no_button = tk.Button(add_new_contact_confirmation_window, text="No", bg="grey", fg="black", font=("Calibri", 10), justify="right", command=lambda: close_window(add_new_contact_confirmation_window))
    accept_contact_confirmation_no_button.place(relx=0.5, rely=0.6, relheight=0.4, relwidth=0.25)


def add_contacts():
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

    contacts_cancelling_button = tk.Button(add_contacts_window, text="Cancel", bg="grey", fg="black", font=("Calibri", 10), justify="right", command=lambda: close_window(add_contacts_window))
    contacts_cancelling_button.place(relx=0.8, rely=0.9, relheight=0.1, relwidth=0.2)

    info_label = tk.Label(add_contacts_window, text="Click a name to add to contacts:", bg="yellow", bd=4)
    info_label.place(relx=0, rely=0.9, relheight=0.1, relwidth=0.8)

    list_of_all_users = []

    # Filling the list of all other users apart from the current one
    with open('users.csv', 'r') as users_file:
        csv_reader = csv.DictReader(users_file)
        for entry in csv_reader:
            if entry["name"] != USER_NAME:
                list_of_all_users.append(entry["name"])

    # Creating new buttons with the corresponding label for each contact
    for index, user in enumerate(list_of_all_users):
        button = tk.Button(add_contacts_space_for_buttons, text=user, bg="grey", fg="black", font=("Calibri", 10), justify="center", command=lambda user=user: add_new_contact_confirmation(user))
        button.place(relx=0, rely=(0.11 * index),relheight=0.1, relwidth=1)

# Accepts a new contact, updates the requests and closes the confirmation window
def accept_new_contact_and_close_dialog(user_name):
    accept_contact_request(user_name)
    populate_contact_requests()
    close_window(accept_contact_request_confirmation_window)

# Confirms whether user really wants to accept contact
def accept_contact_request_confirmation(user_name):
    global accept_contact_request_confirmation_window
    accept_contact_request_confirmation_window = tk.Toplevel(main_window)
    accept_contact_request_confirmation_window.title("Accept contact request?")
    accept_contact_request_confirmation_window.geometry("500x200")

    text_in_the_label = "Do you really want to add user \"{}\" to the contacts?".format(user_name)

    accept_contact_confirmation_label = tk.Label(accept_contact_request_confirmation_window, text=text_in_the_label, bg="yellow", font=("Calibri", 15), anchor="nw", justify="left", bd=4)
    accept_contact_confirmation_label.place(relx=0, rely=0, relheight=0.5, relwidth=1)

    accept_contact_confirmation_yes_button = tk.Button(accept_contact_request_confirmation_window, text="Yes", bg="grey", fg="black", font=("Calibri", 10), justify="right", command=lambda: accept_new_contact_and_close_dialog(user_name))
    accept_contact_confirmation_yes_button.place(relx=0.2, rely=0.6, relheight=0.4, relwidth=0.25)

    accept_contact_confirmation_no_button = tk.Button(accept_contact_request_confirmation_window, text="No", bg="grey", fg="black", font=("Calibri", 10), justify="right", command=lambda: close_window(accept_contact_request_confirmation_window))
    accept_contact_confirmation_no_button.place(relx=0.5, rely=0.6, relheight=0.4, relwidth=0.25)

# Populates the list of cotnact requests
def populate_contact_requests():
    # Deleting all the previous buttons with contacts if they exist
    for button in manage_contacts_space_for_buttons.winfo_children():
        button.destroy()

    list_of_users_requesting_contact = []

    # Filling the list of all other users apart from the current one
    with open('contact_requests.csv', 'r') as contact_requests_file:
        csv_reader = csv.DictReader(contact_requests_file)
        for entry in csv_reader:
            if entry["other_user"] == USER_NAME:
                list_of_users_requesting_contact.append(entry["sender_user"])

    # Creating new buttons with the corresponding label for each contact
    for index, user in enumerate(list_of_users_requesting_contact):
        button = tk.Button(manage_contacts_space_for_buttons, text=user, bg="grey", fg="black", font=("Calibri", 10), justify="center", command=lambda user=user: accept_contact_request_confirmation(user))
        button.place(relx=0, rely=(0.1 * index),relheight=0.1, relwidth=1)

def manage_contact_requests():
    global manage_contacts_window
    manage_contacts_window = tk.Toplevel(main_window)
    manage_contacts_window.title("Manage contacts requests")
    manage_contacts_window.geometry("600x600")

    global manage_contacts_space_for_buttons
    manage_contacts_space_for_buttons = tk.Text(manage_contacts_window, bg="yellow", bd=4)
    manage_contacts_space_for_buttons.place(relx=0, rely=0.1, relheight=0.8, relwidth=1)

    contacts_cancelling_button = tk.Button(manage_contacts_window, text="Cancel", bg="grey", fg="black", font=("Calibri", 10), justify="right", command=lambda: close_window(manage_contacts_window))
    contacts_cancelling_button.place(relx=0.8, rely=0.9, relheight=0.1, relwidth=0.2)

    info_label = tk.Label(manage_contacts_window, text="Click a name to add to contacts:", bg="yellow", bd=4)
    info_label.place(relx=0, rely=0.9, relheight=0.1, relwidth=0.8)

    populate_contact_requests()

def handle_closing_login_windows(result, user_name):
    # close_window(login_result_window)
    if result == "SUCCESS":
        try:
            close_window(login_window)
        except:
            pass

        # Populating all the fields in the beginning
        populate_name(user_name)
        load_mood(user_name)

        messaging_label["state"] = "normal" # enabling to manipulate its content
        messaging_label.delete("1.0", "end")
        messaging_label.insert("insert", "Please choose a contact to start a conversation!")
        messaging_label["state"] = "disabled" # disabling the content for user manipulation

        populate_contacts()
    else:
        reset_login(login_result_window)

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
    user_name = login_user_name_entry.get()
    password = login_password_entry.get()

    message=""

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

    show_result_from_login(message, user_name)

# Deletes the content of user_name and password and if asked to, closes the handling dialog
def reset_login(dialog_to_close=None):
    if dialog_to_close is not None:
        close_window(dialog_to_close)
    login_user_name_entry.delete(0, "end")
    login_password_entry.delete(0, "end")


def login_screen():
    global login_window
    login_window = tk.Toplevel(main_window)
    login_window.title("Login")
    login_window.geometry("500x300")

    login_label = tk.Label(login_window, text="Please enter you login details:", bg="yellow", font=("Calibri", 15), anchor="nw", justify="left", bd=4)
    login_label.place(relheight=0.2, relwidth=1)

    login_user_name_label = tk.Label(login_window, text="User name:", bg="yellow", font=("Calibri", 15), anchor="nw", justify="left", bd=4)
    login_user_name_label.place(relx=0.05, rely=0.2, relheight=0.2, relwidth=0.3)

    global login_user_name_entry
    login_user_name_entry = tk.Entry(login_window, bg="orange", font=("Calibri", 15), bd=5)
    login_user_name_entry.place(relx=0.4, rely=0.2, relheight=0.2, relwidth=0.55)

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

def handle_closing_register_windows(user_name, result):
    close_window(register_result_window)
    if result == "SUCCESS":
        close_window(register_window)
        handle_closing_login_windows("SUCCESS", user_name)
    else:
        reset_register(register_result_window)

# TODO: probably generalize this as a "showing_results" function for both login and register
def show_result_from_register(user_name, result):
    global register_result_window
    register_result_window = tk.Toplevel(login_window)
    register_result_window.title("Login result")
    register_result_window.geometry("400x200")

    text = ""

    if result == "SUCCESS":
        text = "Registration successful, welcome!"
    elif result == "NOT SAME PASSWORD":
        text = "Passwords are not the same! Registration failed, please try again!"
    elif result == "USER ALREADY EXISTS":
        text = "User with the name {} already exists! Registration failed, please try again!".format(user_name)

    login_result_label = tk.Label(register_result_window, text=text, bg="yellow", font=("Calibri", 15), anchor="nw", justify="left", bd=4)
    login_result_label.place(relx=0.1, rely=0.1, relheight=0.5, relwidth=0.8)

    login_result_button = tk.Button(register_result_window, text="Close", bg="yellow", font=("Calibri", 15), anchor="nw", justify="left", bd=4, command=lambda: handle_closing_register_windows(user_name, result))
    login_result_button.place(relx=0.4, rely=0.75, relheight=0.2, relwidth=0.2)

def register_into_application():
    user_name = register_user_name_entry.get()
    password = register_password_entry.get()
    password_verify = register_password_entry_verify.get()

    # Checking if the password was typed both times the same
    if (password != password_verify):
        show_result_from_register(user_name, "NOT SAME PASSWORD")
        return

    # Checking if there is not already a user with the same name
    with open('users.csv', 'r') as users_file:
        user_list = csv.DictReader(users_file)
        # Looping through the users and looking for the same USER_NAME
        for user in user_list:
            if user['name'] == user_name:
                show_result_from_register(user_name, "USER ALREADY EXISTS")
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

    show_result_from_register(user_name, "SUCCESS")

def reset_register():
    register_user_name_entry.delete(0, "end")
    register_password_entry.delete(0, "end")
    register_password_entry_verify.delete(0, "end")

def register_screen():
    global register_window
    register_window = tk.Toplevel(main_window)
    register_window.title("Login")
    register_window.geometry("500x300")

    register_label = tk.Label(register_window, text="Please enter you details:", bg="yellow", font=("Calibri", 15), anchor="nw", justify="left", bd=4)
    register_label.place(relheight=0.2, relwidth=1)

    register_user_name_label = tk.Label(register_window, text="User name:", bg="yellow", font=("Calibri", 15), anchor="nw", justify="left", bd=4)
    register_user_name_label.place(relx=0.05, rely=0.15, relheight=0.15, relwidth=0.3)

    global register_user_name_entry
    register_user_name_entry = tk.Entry(register_window, bg="orange", font=("Calibri", 15), bd=5)
    register_user_name_entry.place(relx=0.4, rely=0.15, relheight=0.15, relwidth=0.55)

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
    user_name = USER_NAME

    users_file = pd.read_csv("users.csv")
    users_file.loc[users_file["name"]==user_name, "mood"] = mood
    users_file.to_csv("users.csv", index=False)

    # Showing the change to the user and closing the editing window
    load_mood(user_name, mood)
    close_window(edit_mood_window)

def log_out_from_application():
    global USER_NAME
    USER_NAME=""
    print("logging off")

    # Deleting the text in name and mood labels
    name_label["text"] = ""
    mood_label["text"] = ""

    # Emptying all the messages in the label
    messaging_label["state"] = "normal" # enabling to manipulate its content
    messaging_label.delete("1.0", "end")
    messaging_label["state"] = "disabled" # disabling the content for user manipulation

    # Deleting all the buttons with contacts
    for widget in contact_space_for_buttons.winfo_children():
        widget.destroy()

# Serves to quickly see if user has some new contact requests
def update_manage_requests():
    list_of_users_requesting_contact = []

    # Filling the list of all other users apart from the current one
    with open('contact_requests.csv', 'r') as contact_requests_file:
        csv_reader = csv.DictReader(contact_requests_file)
        for entry in csv_reader:
            if entry["other_user"] == USER_NAME:
                list_of_users_requesting_contact.append(entry["sender_user"])

    requests_amount = len(list_of_users_requesting_contact)

    contact_requests_button["text"] = "Manage requests ({})".format(requests_amount)

# Is saving the last time user was sending an updating request (was online)
def log_last_time_online(user_name):
    current_timestamp = int(time.time())

    users_file = pd.read_csv("users.csv")
    users_file.loc[users_file["name"]==user_name, "last_time_online"] = current_timestamp
    users_file.to_csv("users.csv", index=False)

# Defining the main window and its title
main_window = tk.Tk()
main_window.state('zoomed') # Making the window maximized
main_window.title(TITLE)

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

messaging_button = tk.Button(messaging_area, text="Send", bg="grey", fg="black", font=("Calibri", 10), justify="center", command=lambda: send_message(messaging_text.get("1.0", "end-1c"), CURRENT_CONVERSATION_ID))
messaging_button.place(relx=0.8, rely=0.8,relheight=0.2, relwidth=0.2)


# CONTACTS PART
contacts_area = tk.Frame(main_window, bg="#42b6f4", bd=10)
contacts_area.place(relx=0.05, rely=0.3, relwidth=0.2, relheight=0.65)

# contact_space_for_buttons = tk.Label(contacts_area, bg="yellow", font=("Calibri", 15), anchor="nw", justify="left", bd=4)
contact_space_for_buttons = tk.Text(contacts_area, bg="yellow", font=("Calibri", 15), bd=4)
contact_space_for_buttons.place(relheight=0.9, relwidth=1)

contact_new_button = tk.Button(contacts_area, text="Add new contacts", bg="grey", fg="black", font=("Calibri", 10), justify="center", command=lambda: add_contacts())
contact_new_button.place(relx=0, rely=0.8,relheight=0.1, relwidth=1)

contact_requests_button = tk.Button(contacts_area, text="Manage requests", bg="grey", fg="black", font=("Calibri", 10), justify="center", command=lambda: manage_contact_requests())
contact_requests_button.place(relx=0, rely=0.9,relheight=0.1, relwidth=1)


# Saving time with no login :)
handle_closing_login_windows("SUCCESS", "123")


# # Running all the update functions in regular time intervals
while True:
    print("UPDATING")
    update_manage_requests()
    time.sleep(5)

# s = sched.scheduler(time.time, time.sleep)
# def do_something(sc):
#     print( "Doing stuff...")
#     update_manage_requests()
#     s.enter(5, 1, do_something, (sc,))
#
# s.enter(5, 1, do_something, (s,))
# s.run()

#
def update_the_page():
    print("UPDATING")
    populate_contacts()
    update_manage_requests()
    populate_messages(CURRENT_CONVERSATION_ID, CURRENTLY_OPENED_CONTACT_NAME)
    log_last_time_online(USER_NAME)
    main_window.after(3000, update_the_page)

update_the_page()


main_window.mainloop()
