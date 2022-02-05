import csv
import datetime
import os
import random
import re
import time
import tkinter as tk
from tkinter import font

import mysql.connector
import pandas as pd
from mysql.connector import Error

TITLE = "Chatting App"

# USER_NAME will be stored globally, to be accessible easily everywhere
# Will get initialised right after user authenticates
USER_NAME = ""

CURRENTLY_OPENED_CONTACT_NAME = ""
CURRENTLY_OPENED_CONTACT_MOOD = ""
CURRENT_CONVERSATION_ID = 0

# In this dictionary we will store for each conversation the timestamp of the
#   last message that we are storing offline.
# Structure: {"conv_id": "timestamp"} ... {1: 1557869354, 4: 1562356847}
LAST_TIMESTAMPS_IN_CONVERSATIONS = {}

try:
    connection = mysql.connector.connect(
        host="89.221.219.124", database="chat", user="user", password="password"
    )
    if connection.is_connected():
        db_Info = connection.get_server_info()
        # print("Connected to MySQL database... MySQL Server version on ",db_Info)
        cursor = connection.cursor(named_tuple=True)
        # cursor.execute("select database();")
        # record = cursor.fetchone()
        # print ("Your connected to - ", record)
except Error as e:
    print("Error while connecting to MySQL", e)


# Helper function to fill a text component with a content in a safe way
# Possible modes: "rewrite" - fill it completely from the scratch,
#   "append" - just appending the specified content to already existing one
def define_text_content(text_component, content_to_fill, mode="rewrite"):
    text_component["state"] = "normal"  # enabling to manipulate the content
    if mode == "rewrite":
        text_component.delete("1.0", "end")  # deleting the whole previous content
    text_component.insert("insert", content_to_fill)  # inserting completely new content
    text_component["state"] = "disabled"  # disabling the content for user manipulation


# Helper function that is closing a specific window
def close_window(window_name):
    window_name.destroy()  # closing the specified window


# General window that is just displaying whatever text is supplied to it
def show_message_to_user(message_content):
    show_message_window = tk.Toplevel(main_window)
    show_message_window.title("Message")
    show_message_window.geometry("500x200")

    show_message_text = tk.Text(
        show_message_window, bg="yellow", font=("Calibri", 15), bd=4
    )
    show_message_text.place(relheight=1, relwidth=1)

    show_message_cancelling_button = tk.Button(
        show_message_text,
        text="Cancel",
        bg="grey",
        font=("Calibri", 15),
        command=lambda: close_window(show_message_window),
    )
    show_message_cancelling_button.place(
        relx=0.7, rely=0.7, relheight=0.3, relwidth=0.3
    )

    # Filling the text with a suplied message
    show_message_text.insert("insert", message_content)
    show_message_text["state"] = "disabled"


# Filling the name to be displayed and setting the global USER_NAME
# Having non-empty USER_NAME means somebody is logged in
def populate_name(name):
    global USER_NAME
    USER_NAME = name
    name_label["text"] = name


# Display the current user's mood
def populate_mood(mood):
    mood_label["text"] = mood


# Filling the list of contacts, each as sequence of buttons
def populate_contacts():
    # Finding out the number of already having contacts (each contact has 3 widgets)
    number_of_contacts_rendered = len(contact_space_for_buttons.winfo_children()) / 3

    # Getting the list of all contacts of current user
    contact_list = []

    query = "SELECT * from conversations WHERE user_1_name = '{}' or user_2_name = '{}';".format(
        USER_NAME, USER_NAME
    )
    cursor.execute(query)
    result = cursor.fetchall()

    # Getting array of all names (for the search in users table)
    all_contact_names = []
    for conversation in list(result):
        other_name = (
            conversation.user_2_name
            if conversation.user_2_name != USER_NAME
            else conversation.user_1_name
        )
        all_contact_names.append(other_name)
        contact_list.append(
            {"name": other_name, "conversation_id": conversation.conversation_id}
        )

    for index, contact in enumerate(contact_list):
        query = "SELECT mood, last_time_online from users WHERE name = '{}';".format(
            contact["name"]
        )
        cursor.execute(query)
        result = cursor.fetchone()

        contact_list[index]["last_time_online"] = result.last_time_online
        contact_list[index]["mood"] = result.mood

    # Current timestamp will be used in both branches, so calculate it beforehand
    current_timestamp = int(time.time())

    # When the number of rendered contact does not correspond to the number of fetched
    #   contacts, re-render the whole contact view
    # Otherwise we will just update the current widgets
    if number_of_contacts_rendered != len(contact_list):
        # Deleting all the previous buttons with contacts if they exist
        for button in contact_space_for_buttons.winfo_children():
            button.destroy()

        # Creating new buttons with the corresponding label for each contact
        for index, user in enumerate(contact_list):
            user_name = user["name"]
            user_mood = user["mood"]
            conversation_id = user["conversation_id"]
            last_user_timestamp = user["last_time_online"]

            # Determining how long time passed from the user being online the last time
            time_from_last_online_state = current_timestamp - last_user_timestamp

            # Setting label's colour according to the last online date
            label_background_color = ""
            if time_from_last_online_state < 60:
                label_background_color = "green"
            elif time_from_last_online_state < 300:
                label_background_color = "orange"
            else:
                label_background_color = "red"

            # Label that is visually showing whether the user is online or not
            online_status_label = tk.Label(
                contact_space_for_buttons, text="", bg=label_background_color
            )
            online_status_label.place(
                relx=0, rely=(0.11 * index), relheight=0.1, relwidth=0.2
            )

            button_with_contact_user_name = tk.Button(
                contact_space_for_buttons,
                text=user_name,
                bg="grey",
                font=("Calibri", 15),
                justify="center",
                command=lambda conversation_id=conversation_id, user_name=user_name, user_mood=user_mood: populate_conversation(
                    conversation_id, user_name, user_mood
                ),
            )
            button_with_contact_user_name.place(
                relx=0.25, rely=(0.11 * index), relheight=0.1, relwidth=0.5
            )

            info_button = tk.Button(
                contact_space_for_buttons,
                text="INFO",
                bg="grey",
                font=("Calibri", 15),
                justify="center",
                command=lambda user_name=user_name: show_user_info_screen(user_name),
            )
            info_button.place(
                relx=0.8, rely=(0.11 * index), relheight=0.1, relwidth=0.2
            )
    else:
        # Updating the colour of the label, signalling on/off-line state of contacts
        index = 0
        for component in contact_space_for_buttons.winfo_children():
            # Choosing only labels from all the children
            if component.winfo_class() == "Label":
                last_user_timestamp = contact_list[index]["last_time_online"]

                # Determining how long time passed from the user being online the last time
                time_from_last_online_state = current_timestamp - last_user_timestamp

                # Setting label's colour according to the last online date
                label_background_color = ""
                if time_from_last_online_state < 60:
                    label_background_color = "green"
                elif time_from_last_online_state < 300:
                    label_background_color = "orange"
                else:
                    label_background_color = "red"

                component["bg"] = label_background_color
                index += 1


# Opens a window with the information about a specific user
def show_user_info_screen(user_name):
    show_user_info_window = tk.Toplevel(main_window)
    show_user_info_window.title("User info")
    show_user_info_window.geometry("400x200")

    label_text = "{}'s information:".format(user_name)

    query = "SELECT mood, last_time_online from users WHERE name = '{}';".format(
        user_name
    )
    cursor.execute(query)
    result = cursor.fetchone()

    user_mood = result.mood
    last_time_online = result.last_time_online

    # Transforming the UNIX timestamp into a human friendly date
    human_readable_last_time_online = datetime.datetime.fromtimestamp(
        last_time_online
    ).strftime("%Y-%m-%d %H:%M:%S")

    mood_label_text = "Mood: {}".format(user_mood)
    last_time_online_text = "Last time online: {}".format(
        human_readable_last_time_online
    )

    show_user_info_label = tk.Label(
        show_user_info_window,
        text=label_text,
        bg="yellow",
        font=("Calibri", 15),
        anchor="nw",
        justify="left",
        bd=4,
    )
    show_user_info_label.place(relx=0, rely=0, relheight=0.2, relwidth=1)

    mood_info_label = tk.Label(
        show_user_info_window,
        text=mood_label_text,
        bg="yellow",
        font=("Calibri", 15),
        anchor="nw",
        justify="left",
        bd=4,
    )
    mood_info_label.place(relx=0, rely=0.2, relheight=0.4, relwidth=1)

    timestamp_info_label = tk.Label(
        show_user_info_window,
        text=last_time_online_text,
        bg="yellow",
        font=("Calibri", 15),
        anchor="nw",
        justify="left",
        bd=4,
    )
    timestamp_info_label.place(relx=0, rely=0.6, relheight=0.4, relwidth=1)

    show_user_info_cancelling_button = tk.Button(
        timestamp_info_label,
        text="Cancel",
        bg="grey",
        font=("Calibri", 15),
        command=lambda: close_window(show_user_info_window),
    )
    show_user_info_cancelling_button.place(
        relx=0.7, rely=0.4, relheight=0.6, relwidth=0.3
    )


# Filling the message area with all the messages from a chosen conversation
#   and some other metadata connected with that conversation.
# Also storing the timestamps of reading the messages and possibly typing
def populate_conversation(conversation_id, user_name, user_mood):
    # When no specific conversation is chosen, show the info message and return
    if conversation_id == 0:
        define_text_content(
            messaging_area_text, "Please choose a contact to start a conversation!"
        )
        return

    # Storing the current conversation in the whole program
    global CURRENT_CONVERSATION_ID, CURRENTLY_OPENED_CONTACT_NAME, CURRENTLY_OPENED_CONTACT_MOOD
    CURRENT_CONVERSATION_ID = conversation_id
    CURRENTLY_OPENED_CONTACT_NAME = user_name
    CURRENTLY_OPENED_CONTACT_MOOD = user_mood

    # TODO: implement some synchronization between DB and local files to increase efficiency
    # # Checking if there is already a filename with current conversation,
    # #   and if not, prepare the headers
    # file_path = "Conversations/{}-{}.csv".format(USER_NAME, CURRENTLY_OPENED_CONTACT_NAME)
    # if not os.path.isfile(file_path):
    #     with open(file_path, "w") as conversation_file:
    #         csv_writer = csv.writer(conversation_file)
    #         csv_writer.writerow(["timestamp", "user_name", "message_text"])
    #
    # # Saving all messages into a text variable, ready to be displayed
    # with open(file_path, 'r') as messages_file:
    #     csv_reader = csv.DictReader(messages_file)
    #     for message in csv_reader:
    #         text_messages += "{}: {}\n".format(message["user_name"], message["message_text"])

    query = "SELECT * from messages WHERE conversation_id = '{}'".format(
        conversation_id
    )
    cursor.execute(query)
    result = cursor.fetchall()

    text_messages = ""
    for message in list(result):
        text_messages += "{}: {}\n".format(message.user_name, message.message)

    # If there are no messages yet, display the initial message to break the silence :)
    if text_messages == "":
        text_messages = "Greet your new contact {}!".format(user_name)

    # Filling the text area with all the messages and scrolling to the very bottom
    define_text_content(messaging_area_text, text_messages)
    messaging_area_text.yview_moveto(1)

    # Showing the name and mood of the current contact
    current_contact_label["text"] = "Current contact - {} ({})".format(
        user_name, user_mood
    )

    # Finding out whether the other person displayed the last message
    # Also updating the last time current user has displayed this conversation
    #   and if the text entry is not blank, updating the typing time as well

    query = "SELECT * from conversations WHERE conversation_id = '{}'".format(
        conversation_id
    )
    cursor.execute(query)
    result = cursor.fetchone()

    # Determining if the current user is number 1 or 2 - to know which fields to inspect
    user_number = 1 if result.user_1_name == USER_NAME else 2
    other_user_number = 1 if user_number == 2 else 2

    last_message_timestamp = result.last_message_timestamp
    last_displayed_timestamp = (
        result.last_user_1_read_timestamp
        if other_user_number == 1
        else result.last_user_2_read_timestamp
    )
    last_message_user_name = result.last_message_user_name
    last_typing_timestamp = (
        result.last_user_1_typing_timestamp
        if other_user_number == 1
        else result.last_user_2_typing_timestamp
    )

    # If the other user has displayed the conversation after the last message,
    #   and we were the last messager, show it in a label as "Displayed"
    if (
        last_displayed_timestamp > last_message_timestamp
        and last_message_user_name == USER_NAME
    ):
        message_displayed_label["text"] = "Displayed"
    else:
        message_displayed_label["text"] = ""

    # Getting the current timestamp to verify the typing of the other person
    #   and to log the last displayed timestamp of the current user
    current_timestamp = int(time.time())

    # If the other user has been typing in the last 3 seconds, display that
    if current_timestamp - last_typing_timestamp <= 3:
        message_typing_label["text"] = "Typing..."
    else:
        message_typing_label["text"] = ""

    # Updating the corresponding read-field with a current timestamp
    query = "UPDATE conversations SET last_user_{}_read_timestamp='{}' WHERE conversation_id = '{}'".format(
        user_number, current_timestamp, conversation_id
    )
    cursor.execute(query)
    connection.commit()
    # conversations_table.loc[conversations_table["conv_id"]==conversation_id, "last_user_{}_read_timestamp".format(user_number)] = current_timestamp

    # When the user has some text in the message entry, update his last typing timestamp
    if messaging_text.get("1.0", "end-1c") != "":
        query = "UPDATE conversations SET last_user_{}_typing_timestamp='{}' WHERE conversation_id = '{}'".format(
            user_number, current_timestamp, conversation_id
        )
        cursor.execute(query)
        connection.commit()


# Sending a message - saving it to the text file
# Also updating the conversation table and storing the time of message as a last timestamp
# Last but not least logging the current user as a last messager of that conversation
def send_message(message, conversation_id):
    # If some basic error handling and defence against invalid inputs
    if conversation_id == 0:
        show_message_to_user(
            "It is better to chat with somebody.\nPlease choose some of your contacts."
        )
        return
    elif message == "":
        show_message_to_user("You certainly wanted to write something more :)")
        return

    current_timestamp = int(time.time())

    # Appending the new message to a messages table
    query = """INSERT INTO messages (conversation_id, timestamp, user_name, message)
            VALUES ('{}', '{}', '{}', '{}');
            """.format(
        conversation_id, current_timestamp, USER_NAME, message
    )
    cursor.execute(query)
    connection.commit()

    # Storing the new last timestamp and last user in conversation table
    query = """UPDATE conversations SET last_message_timestamp = '{}', last_message_user_name = '{}'
                WHERE conversation_id = '{}';
            """.format(
        current_timestamp, USER_NAME, conversation_id
    )
    cursor.execute(query)
    connection.commit()

    # # Checking if there is already a filename with current conversation,
    # #   and if not, write the headers and content
    # # Otherwise append the new message
    # file_path = "Conversations/{}-{}.csv".format(USER_NAME, CURRENTLY_OPENED_CONTACT_NAME)
    # if not os.path.isfile(file_path):
    #     with open(file_path, "w") as conversation_file:
    #         csv_writer = csv.writer(conversation_file)
    #         csv_writer.writerow(["timestamp", "user_name", "message_text"])
    #         csv_writer.writerow([current_timestamp, USER_NAME, message])
    # else:
    #     with open(file_path, "a") as conversation_file:
    #         csv_writer = csv.writer(conversation_file)
    #         csv_writer.writerow([current_timestamp, USER_NAME, message])

    # Deleting the entry field
    messaging_text.delete("1.0", "end")

    # Updating the text in message window
    # TODO: If there is the initial message, do not append it, but delete that first message
    new_message = "{}: {}\n".format(USER_NAME, message)
    define_text_content(messaging_area_text, new_message, "append")
    messaging_area_text.yview_moveto(1)

    # Populating the message label with a new content
    # TODO: do not refresh everything, just add a new line, and store it locally
    # populate_conversation(CURRENT_CONVERSATION_ID, CURRENTLY_OPENED_CONTACT_NAME, CURRENTLY_OPENED_CONTACT_MOOD)


# Saves the settings after some changes
def save_new_settings():
    print("save new settings")


# Shows a window with all the defined settings
def show_settings_screen():
    settings_window = tk.Toplevel(main_window)
    settings_window.title("Add settings")
    settings_window.geometry("600x400")

    settings_label = tk.Label(
        settings_window,
        text="Choose your settings:",
        bg="yellow",
        font=("Calibri", 15),
        anchor="nw",
        justify="left",
        bd=4,
    )
    settings_label.place(relheight=1, relwidth=1)

    settings_saving_button = tk.Button(
        settings_label,
        text="Save new settings",
        bg="grey",
        font=("Calibri", 15),
        command=lambda: save_new_settings(),
    )
    settings_saving_button.place(relx=0, rely=0.9, relheight=0.1, relwidth=0.2)

    contacts_cancelling_button = tk.Button(
        settings_label,
        text="Cancel",
        bg="grey",
        font=("Calibri", 15),
        command=lambda: close_window(settings_window),
    )
    contacts_cancelling_button.place(relx=0.8, rely=0.9, relheight=0.1, relwidth=0.2)


# Rejecting the contact request and deleting it from the contact_requests table
def delete_contact_request(user_name):
    # Making sure all the requests with those two user_names are deleted
    query = """DELETE FROM contact_requests WHERE
                    (sender_user='{}' AND other_user='{}' )
                    or (other_user='{}' AND sender_user='{}');
                    """.format(
        user_name, USER_NAME, user_name, USER_NAME
    )
    cursor.execute(query)
    connection.commit()


# Accepts the request to be added as a contact
# Removing the request from contact_requests and creating a new conversation in conversations
# After successful saving of everything, reload the contacts bar to show the new conversation
def accept_contact_request(user_name):
    # Deleting all contact requests between those two users
    delete_contact_request(user_name)

    query = "INSERT INTO conversations (user_1_name, user_2_name) VALUES ('{}', '{}');".format(
        user_name, USER_NAME
    )
    cursor.execute(query)
    connection.commit()

    # Updating the contact section to include the new contact
    populate_contacts()


# Sends request to some other user to be added as a contact
def send_contact_request(user_name):
    # Check if these two people already do not share a conversation - otherwise do not continue
    query = """SELECT conversation_id from conversations WHERE
                (user_1_name = '{}' and user_2_name = '{}') or
                (user_2_name = '{}' and user_1_name = '{}')
            """.format(
        user_name, USER_NAME, user_name, USER_NAME
    )
    cursor.execute(query)
    result = cursor.fetchone()

    # If those two users are already connected, notify and return
    if result is not None:
        show_message_to_user("User {} is already in your contacts!".format(user_name))
        return
    else:
        show_message_to_user("Request sent!")

    query = "INSERT INTO contact_requests (sender_user, other_user) VALUES ('{}', '{}')".format(
        USER_NAME, user_name
    )
    cursor.execute(query)
    connection.commit()


# Accepts a new contact, updates the requests and closes the confirmation window
def add_new_contact_and_close_dialog(user_name, dialog_to_close):
    send_contact_request(user_name)
    close_window(dialog_to_close)


# General confirmation dialog
# If confirmed, performs a function with given arguments, otherwise just closes this window.
# WARNING: The yes_function must be equipped with window-closing ability
def confirmation_dialog(shown_message, yes_function, yes_args):
    global CONFIRMATION_WINDOW
    CONFIRMATION_WINDOW = tk.Toplevel(main_window)
    CONFIRMATION_WINDOW.title("Confirmation window")
    CONFIRMATION_WINDOW.geometry("500x200")

    confirmation_text = tk.Text(
        CONFIRMATION_WINDOW, bg="yellow", font=("Calibri", 15), bd=4
    )
    confirmation_text.place(relx=0, rely=0, relheight=1, relwidth=1)

    confirmation_yes_button = tk.Button(
        confirmation_text,
        text="Yes",
        bg="grey",
        font=("Calibri", 15),
        command=lambda: yes_function(yes_args, CONFIRMATION_WINDOW),
    )
    confirmation_yes_button.place(relx=0.2, rely=0.6, relheight=0.4, relwidth=0.25)

    confirmation_no_button = tk.Button(
        confirmation_text,
        text="No",
        bg="grey",
        font=("Calibri", 15),
        command=lambda: close_window(CONFIRMATION_WINDOW),
    )
    confirmation_no_button.place(relx=0.5, rely=0.6, relheight=0.4, relwidth=0.25)

    # Filling the text with supplied message
    confirmation_text.insert("insert", shown_message)
    confirmation_text["state"] = "disabled"


# Creates a list of application's users, and outputs it to some component
# Has a form of a label with a name, button to show information about
#   a specific user, and a button to add this user to the contacts
def show_users(component_where_to_put_it, search_pattern=None):
    # Deleting all the previous user's buttons, if there were some
    for button in component_where_to_put_it.winfo_children():
        button.destroy()

    # Filling the list of all other users apart from the current one
    # When search pattern is applied, also filter it with that
    if search_pattern is None:
        query = "SELECT name from users WHERE name != '{}'".format(USER_NAME)
    else:
        query = """SELECT name from users WHERE name != '{}' and name LIKE '%{}%'""".format(
            USER_NAME, search_pattern
        )
    cursor.execute(query)
    result = cursor.fetchall()

    list_of_users = []
    for person in result:
        list_of_users.append(person.name)

    # Creating new labels and buttons with the corresponding label for each
    #   contact that passed the filter
    for index, user_name in enumerate(list_of_users):
        user_label = tk.Label(
            component_where_to_put_it,
            text=user_name,
            bg="grey",
            fg="black",
            font=("Calibri", 15),
            justify="center",
        )
        user_label.place(relx=0, rely=(0.11 * index), relheight=0.1, relwidth=0.5)

        user_info_button = tk.Button(
            component_where_to_put_it,
            text="INFO",
            bg="orange",
            fg="black",
            font=("Calibri", 15),
            justify="center",
            command=lambda user_name=user_name: show_user_info_screen(user_name),
        )
        user_info_button.place(
            relx=0.55, rely=(0.11 * index), relheight=0.1, relwidth=0.2
        )

        user_add_button = tk.Button(
            component_where_to_put_it,
            text="ADD",
            bg="green",
            fg="black",
            font=("Calibri", 15),
            justify="center",
            command=lambda user_name=user_name: confirmation_dialog(
                "Do you really want to add {} as a new contact?".format(user_name),
                add_new_contact_and_close_dialog,
                user_name,
            ),
        )
        user_add_button.place(
            relx=0.8, rely=(0.11 * index), relheight=0.1, relwidth=0.2
        )

    # If the user is asking for all contacts, delete the search entry not to be confusing
    if search_pattern is None:
        CONTACTS_SEARCH_ENTRY.delete(0, "end")


# Creates a window for browsing all users and adding new contacts
def add_contacts_screen():
    global ADD_CONTACTS_WINDOW
    ADD_CONTACTS_WINDOW = tk.Toplevel(main_window)
    ADD_CONTACTS_WINDOW.title("Add contacts")
    ADD_CONTACTS_WINDOW.geometry("600x400")

    add_contacts_label = tk.Label(
        ADD_CONTACTS_WINDOW,
        text="Type the friend's name (or its part):",
        font=("Calibri", 15),
        bg="yellow",
        bd=4,
    )
    add_contacts_label.place(relx=0, rely=0, relheight=0.1, relwidth=1)

    global CONTACTS_SEARCH_ENTRY
    CONTACTS_SEARCH_ENTRY = tk.Entry(
        ADD_CONTACTS_WINDOW, bg="orange", font=("Calibri", 15), bd=5
    )
    CONTACTS_SEARCH_ENTRY.place(relx=0, rely=0.1, relheight=0.1, relwidth=0.7)

    contacts_searching_button = tk.Button(
        ADD_CONTACTS_WINDOW,
        text="Search",
        bg="grey",
        fg="black",
        font=("Calibri", 15),
        command=lambda: show_users(
            ADD_CONTACTS_SPACE_FOR_BUTTONS, CONTACTS_SEARCH_ENTRY.get()
        ),
    )
    contacts_searching_button.place(relx=0.7, rely=0.1, relheight=0.1, relwidth=0.3)

    global ADD_CONTACTS_SPACE_FOR_BUTTONS
    ADD_CONTACTS_SPACE_FOR_BUTTONS = tk.Text(
        ADD_CONTACTS_WINDOW, bg="yellow", bd=4, state="disabled"
    )
    ADD_CONTACTS_SPACE_FOR_BUTTONS.place(relx=0, rely=0.2, relheight=0.7, relwidth=1)

    show_all_users_button = tk.Button(
        ADD_CONTACTS_WINDOW,
        text="Show all users",
        bg="grey",
        fg="black",
        font=("Calibri", 15),
        command=lambda: show_users(ADD_CONTACTS_SPACE_FOR_BUTTONS),
    )
    show_all_users_button.place(relx=0, rely=0.9, relheight=0.1, relwidth=0.2)

    contacts_cancelling_button = tk.Button(
        ADD_CONTACTS_WINDOW,
        text="Cancel",
        bg="grey",
        fg="black",
        font=("Calibri", 15),
        command=lambda: close_window(ADD_CONTACTS_WINDOW),
    )
    contacts_cancelling_button.place(relx=0.8, rely=0.9, relheight=0.1, relwidth=0.2)

    info_label = tk.Label(ADD_CONTACTS_WINDOW, text="", bg="yellow", bd=4)
    info_label.place(relx=0.2, rely=0.9, relheight=0.1, relwidth=0.6)


# Accepts a new contact, updates the requests and closes the confirmation window
def accept_new_contact_and_close_dialog(user_name, dialog_to_closed):
    accept_contact_request(user_name)
    populate_contact_requests(MANAGE_CONTACT_SPACE_FOR_BUTTONS)
    close_window(dialog_to_closed)


# Accepts a new contact, updates the requests and closes the confirmation window
def reject_new_contact_and_close_dialog(user_name, dialog_to_closed):
    delete_contact_request(user_name)
    populate_contact_requests(MANAGE_CONTACT_SPACE_FOR_BUTTONS)
    close_window(dialog_to_closed)


# Populates the list of contact requests
def populate_contact_requests(component_where_to_put_it):
    # Deleting all the previous buttons with contacts and a text if they exist
    component_where_to_put_it.delete("1.0", "end")
    for button in component_where_to_put_it.winfo_children():
        button.destroy()

    list_of_users_requesting_contact = []

    query = """SELECT sender_user from contact_requests WHERE other_user = '{}';""".format(
        USER_NAME
    )
    cursor.execute(query)
    result = cursor.fetchall()

    for request in result:
        list_of_users_requesting_contact.append(request.sender_user)
    #
    # # Filling the list of all other users apart from the current one
    # with open('contact_requests.csv', 'r') as contact_requests_table:
    #     csv_reader = csv.DictReader(contact_requests_table)
    #     for entry in csv_reader:
    #         if entry["other_user"] == USER_NAME:
    #             list_of_users_requesting_contact.append(entry["sender_user"])

    # If there are no requests for this user, show him an encouraging message
    if len(list_of_users_requesting_contact) < 1:
        cheerful_message = 'Seems nobody wants to add you to contacts.\nWhy don\'t you try to add somebody clicking "Add contacts" button?'
        define_text_content(component_where_to_put_it, cheerful_message)

    # Creating new buttons with the corresponding label for each contact
    for index, user_name in enumerate(list_of_users_requesting_contact):
        button = tk.Label(
            component_where_to_put_it,
            text=user_name,
            bg="grey",
            font=("Calibri", 15),
            justify="center",
        )
        button.place(relx=0, rely=(0.1 * index), relheight=0.1, relwidth=0.5)

        accept_button = tk.Button(
            component_where_to_put_it,
            text="Accept",
            bg="green",
            font=("Calibri", 15),
            justify="center",
            command=lambda user_name=user_name: confirmation_dialog(
                "Do you really want to add {} as a new contact?".format(user_name),
                accept_new_contact_and_close_dialog,
                user_name,
            ),
        )
        accept_button.place(relx=0.55, rely=(0.1 * index), relheight=0.1, relwidth=0.2)
        button.place(relx=0, rely=(0.1 * index), relheight=0.1, relwidth=0.5)

        reject_button = tk.Button(
            component_where_to_put_it,
            text="Reject",
            bg="red",
            font=("Calibri", 15),
            justify="center",
            command=lambda user_name=user_name: confirmation_dialog(
                "Do you really want to reject {}'s contact request?".format(user_name),
                reject_new_contact_and_close_dialog,
                user_name,
            ),
        )
        reject_button.place(relx=0.8, rely=(0.1 * index), relheight=0.1, relwidth=0.2)


# Window for managing contact requests
def manage_contact_requests_screen():
    manage_contacts_window = tk.Toplevel(main_window)
    manage_contacts_window.title("Manage contacts requests")
    manage_contacts_window.geometry("600x600")

    label_text = "List of users who want to add you into contacts:"

    manage_contacts_label = tk.Label(
        manage_contacts_window, text=label_text, font=("Calibri", 15), bg="yellow", bd=4
    )
    manage_contacts_label.place(relx=0, rely=0, relheight=0.1, relwidth=1)

    global MANAGE_CONTACT_SPACE_FOR_BUTTONS
    MANAGE_CONTACT_SPACE_FOR_BUTTONS = tk.Text(
        manage_contacts_window,
        bg="yellow",
        font=("Calibri", 15),
        bd=4,
        state="disabled",
    )
    MANAGE_CONTACT_SPACE_FOR_BUTTONS.place(relx=0, rely=0.1, relheight=0.8, relwidth=1)

    contacts_cancelling_button = tk.Button(
        manage_contacts_window,
        text="Cancel",
        bg="grey",
        font=("Calibri", 15),
        command=lambda: close_window(manage_contacts_window),
    )
    contacts_cancelling_button.place(relx=0.8, rely=0.9, relheight=0.1, relwidth=0.2)

    info_label = tk.Label(manage_contacts_window, text="", bg="yellow", bd=4)
    info_label.place(relx=0, rely=0.9, relheight=0.1, relwidth=0.8)

    populate_contact_requests(MANAGE_CONTACT_SPACE_FOR_BUTTONS)


# Function responsible for logging the user into the application and
#   populating all the user-dependant content
def log_user_into_application(user_name):
    # Finding out the mood
    query = "SELECT mood from users WHERE name = '{}';".format(user_name)
    cursor.execute(query)
    result = cursor.fetchone()

    # Populating all the fields in the beginning
    populate_name(user_name)
    populate_mood(result.mood)
    define_text_content(
        messaging_area_text, "Please choose a contact to start a conversation!"
    )
    populate_contacts()


# Verifies the user-inputted login data and acts accordingly to them
# If they match, log the user in, otherwise notify him with error message
def login_into_application(user_name, password):
    # Finding the user in users table, and verifying his password
    query = "SELECT password from users WHERE name = '{}';".format(user_name)
    cursor.execute(query)
    result = cursor.fetchone()

    # If the user is not found at all, throw error message
    if result is None:
        show_message_to_user("Login failed, please try again!")
        reset_login_entries()
        return

    # If credentials correspond, log user into the application
    if result.password == password:
        show_message_to_user("Login successful, welcome!")
        log_user_into_application(user_name)
        close_window(LOGIN_WINDOW)
        return
    else:
        # If credentials do not match, throw error message
        show_message_to_user("Login failed, please try again!")
        reset_login_entries()
        return


# Deletes the content of user_name and password
def reset_login_entries():
    LOGIN_USER_NAME_ENTRY.delete(0, "end")
    LOGIN_PASSWORD_ENTRY.delete(0, "end")


# Window used to handle the login process
def login_screen():
    global LOGIN_WINDOW
    LOGIN_WINDOW = tk.Toplevel(main_window)
    LOGIN_WINDOW.title("Login")
    LOGIN_WINDOW.geometry("500x300")

    login_label = tk.Label(
        LOGIN_WINDOW,
        text="Please enter your login details:",
        bg="yellow",
        font=("Calibri", 15),
        anchor="nw",
        justify="left",
        bd=4,
    )
    login_label.place(relheight=1, relwidth=1)

    login_user_name_label = tk.Label(
        login_label,
        text="User name:",
        bg="yellow",
        font=("Calibri", 15),
        anchor="nw",
        justify="left",
        bd=4,
    )
    login_user_name_label.place(relx=0.05, rely=0.2, relheight=0.2, relwidth=0.3)

    global LOGIN_USER_NAME_ENTRY
    LOGIN_USER_NAME_ENTRY = tk.Entry(
        login_label, bg="orange", font=("Calibri", 15), bd=5
    )
    LOGIN_USER_NAME_ENTRY.place(relx=0.4, rely=0.2, relheight=0.2, relwidth=0.55)

    login_password_label = tk.Label(
        login_label,
        text="Password:",
        bg="yellow",
        font=("Calibri", 15),
        anchor="nw",
        justify="left",
        bd=4,
    )
    login_password_label.place(relx=0.05, rely=0.5, relheight=0.2, relwidth=0.3)

    global LOGIN_PASSWORD_ENTRY
    LOGIN_PASSWORD_ENTRY = tk.Entry(
        login_label, bg="orange", font=("Calibri", 15), bd=5, show="*"
    )
    LOGIN_PASSWORD_ENTRY.place(relx=0.4, rely=0.5, relheight=0.2, relwidth=0.55)

    login_button_login = tk.Button(
        login_label,
        text="Login",
        bg="grey",
        font=("Calibri", 15),
        command=lambda: login_into_application(
            LOGIN_USER_NAME_ENTRY.get(), LOGIN_PASSWORD_ENTRY.get()
        ),
    )
    login_button_login.place(relx=0.1, rely=0.8, relheight=0.15, relwidth=0.25)

    login_button_reset = tk.Button(
        login_label,
        text="Reset",
        bg="grey",
        font=("Calibri", 15),
        command=lambda: reset_login_entries(),
    )
    login_button_reset.place(relx=0.4, rely=0.8, relheight=0.15, relwidth=0.25)

    login_button_register = tk.Button(
        login_label,
        text="Register",
        bg="grey",
        font=("Calibri", 15),
        command=lambda: register_screen(),
    )
    login_button_register.place(relx=0.7, rely=0.8, relheight=0.15, relwidth=0.25)


# Handles the registration process of a new user
# If successful, it logs the user in authomatically
def register_into_application(user_name, password, password_verify):
    # Checking if the username is not empty
    if user_name == "":
        show_message_to_user(
            "User name cannot be empty!\nRegistration failed, please try again!"
        )
        reset_register()
        return

    # Checking if the password was typed both times the same
    if password != password_verify:
        show_message_to_user(
            "Passwords are not the same!\nRegistration failed, please try again!"
        )
        reset_register()
        return

    # Checking if there is not already a user with the same name
    query = "SELECT name from users WHERE name = '{}'".format(user_name)
    cursor.execute(query)
    result = cursor.fetchall()
    if len(result) > 0:
        show_message_to_user(
            "User with the name {} already exists!\nRegistration failed, please try again!".format(
                user_name
            )
        )
        reset_register()
        return

    # Appending the new user to a users table (if relevant)
    current_timestamp = int(time.time())
    query = """INSERT INTO users (name, mood, last_time_online, date_of_registration,password) VALUES
                                ('{}', 'I have a good mood', '{}', '{}', '{}');
                                """.format(
        user_name, current_timestamp, current_timestamp, password
    )
    cursor.execute(query)
    connection.commit()

    # Showing successful message, and logging the user in
    show_message_to_user(
        "You have been successfully registered!\nYou are now logged in as {}.".format(
            user_name
        )
    )
    log_user_into_application(user_name)

    # Closing all the unnecessary windows
    close_window(REGISTER_WINDOW)
    close_window(LOGIN_WINDOW)


# Empties all the entries in register window
def reset_register():
    REGISTER_USER_NAME_ENTRY.delete(0, "end")
    REGISTER_PASSWORD_ENTRY.delete(0, "end")
    REGISTER_PASSWORD_ENTRY_VERIFY.delete(0, "end")


# Creates a window used for registering of a new user
def register_screen():
    global REGISTER_WINDOW
    REGISTER_WINDOW = tk.Toplevel(main_window)
    REGISTER_WINDOW.title("Login")
    REGISTER_WINDOW.geometry("500x300")

    register_label = tk.Label(
        REGISTER_WINDOW,
        text="Please enter your details:",
        bg="yellow",
        font=("Calibri", 15),
        anchor="nw",
        justify="left",
        bd=4,
    )
    register_label.place(relheight=1, relwidth=1)

    register_user_name_label = tk.Label(
        register_label,
        text="User name:",
        bg="yellow",
        font=("Calibri", 15),
        anchor="nw",
        justify="left",
        bd=4,
    )
    register_user_name_label.place(relx=0.05, rely=0.15, relheight=0.15, relwidth=0.3)

    global REGISTER_USER_NAME_ENTRY
    REGISTER_USER_NAME_ENTRY = tk.Entry(
        register_label, bg="orange", font=("Calibri", 15), bd=5
    )
    REGISTER_USER_NAME_ENTRY.place(relx=0.4, rely=0.15, relheight=0.15, relwidth=0.55)

    register_password_label = tk.Label(
        register_label,
        text="Password:",
        bg="yellow",
        font=("Calibri", 15),
        anchor="nw",
        justify="left",
        bd=4,
    )
    register_password_label.place(relx=0.05, rely=0.35, relheight=0.15, relwidth=0.3)

    global REGISTER_PASSWORD_ENTRY
    REGISTER_PASSWORD_ENTRY = tk.Entry(
        register_label, bg="orange", font=("Calibri", 15), bd=5, show="*"
    )
    REGISTER_PASSWORD_ENTRY.place(relx=0.4, rely=0.35, relheight=0.15, relwidth=0.55)

    register_password_label_verify = tk.Label(
        register_label,
        text="Password again:",
        bg="yellow",
        font=("Calibri", 15),
        anchor="nw",
        justify="left",
        bd=4,
    )
    register_password_label_verify.place(
        relx=0.05, rely=0.55, relheight=0.15, relwidth=0.3
    )

    global REGISTER_PASSWORD_ENTRY_VERIFY
    REGISTER_PASSWORD_ENTRY_VERIFY = tk.Entry(
        register_label, bg="orange", font=("Calibri", 15), bd=5, show="*"
    )
    REGISTER_PASSWORD_ENTRY_VERIFY.place(
        relx=0.4, rely=0.55, relheight=0.15, relwidth=0.55
    )

    register_button_reset = tk.Button(
        register_label,
        text="Reset",
        bg="grey",
        font=("Calibri", 15),
        command=lambda: reset_register(),
    )
    register_button_reset.place(relx=0.4, rely=0.8, relheight=0.15, relwidth=0.25)

    register_button_register = tk.Button(
        register_label,
        text="Register",
        bg="grey",
        font=("Calibri", 15),
        command=lambda: register_into_application(
            REGISTER_USER_NAME_ENTRY.get(),
            REGISTER_PASSWORD_ENTRY.get(),
            REGISTER_PASSWORD_ENTRY_VERIFY.get(),
        ),
    )
    register_button_register.place(relx=0.7, rely=0.8, relheight=0.15, relwidth=0.25)


# Opens a window for the editing of a user's mood
def edit_mood_screen():
    global EDIT_MOOD_WINDOW
    EDIT_MOOD_WINDOW = tk.Toplevel(main_window)
    EDIT_MOOD_WINDOW.title("Edit mood")
    EDIT_MOOD_WINDOW.geometry("400x200")

    mood_label = tk.Label(
        EDIT_MOOD_WINDOW,
        text="Please enter the new mood:",
        bg="yellow",
        font=("Calibri", 15),
        anchor="nw",
        justify="left",
        bd=4,
    )
    mood_label.place(relheight=1, relwidth=1)

    mood_entry = tk.Entry(mood_label, bg="orange", font=("Calibri", 15), bd=5)
    mood_entry.place(relx=0, rely=0.2, relheight=0.4, relwidth=1)

    mood_saving_button = tk.Button(
        mood_label,
        text="Save new mood",
        bg="grey",
        font=("Calibri", 15),
        command=lambda: save_new_mood(mood_entry.get()),
    )
    mood_saving_button.place(relx=0.05, rely=0.7, relheight=0.25, relwidth=0.5)

    mood_cancelling_button = tk.Button(
        mood_label,
        text="Cancel",
        bg="grey",
        font=("Calibri", 15),
        command=lambda: close_window(EDIT_MOOD_WINDOW),
    )
    mood_cancelling_button.place(relx=0.6, rely=0.7, relheight=0.25, relwidth=0.3)


# Changes the mood in the users table
def save_new_mood(mood):
    # Updates the current user's mood in the DB
    query = "UPDATE users SET mood = '{}' WHERE name = '{}';".format(mood, USER_NAME)
    cursor.execute(query)
    connection.commit()

    # Showing the change to the user and closing the editing window
    populate_mood(mood)
    close_window(EDIT_MOOD_WINDOW)


# Logging out from the application
# Emptying all the information and setting all the global variables to emtpy strings
def log_out_from_application():
    global USER_NAME, CURRENT_CONVERSATION_ID, CURRENTLY_OPENED_CONTACT_NAME
    USER_NAME = ""
    CURRENT_CONVERSATION_ID = 0
    CURRENTLY_OPENED_CONTACT_NAME = ""

    # Deleting the text in name and mood labels
    name_label["text"] = ""
    mood_label["text"] = ""

    # Emptying all the messages in the message area and current contact name
    define_text_content(messaging_area_text, "")
    current_contact_label["text"] = "Current contact -"

    # Deleting all the buttons with contacts
    for widget in contact_space_for_buttons.winfo_children():
        widget.destroy()


# Serves to quickly see if user has some new contact requests
def update_number_of_requests():
    # Finding out which users sent contact request to the current user

    query = """SELECT sender_user from contact_requests WHERE other_user = '{}';""".format(
        USER_NAME
    )
    cursor.execute(query)
    result = cursor.fetchall()

    amunt_of_requests = len(result)

    # Displaying the number of requests as a button text
    contact_requests_button["text"] = "Manage requests ({})".format(amunt_of_requests)

    # When there are some new requests, change the button colour to notify the user
    if amunt_of_requests > 0:
        contact_requests_button["bg"] = "red"
    else:
        contact_requests_button["bg"] = "grey"


# Saving the last time user was sending an updating request (was online)
def log_last_time_online(user_name):
    current_timestamp = int(time.time())

    query = "UPDATE users SET last_time_online = '{}' WHERE name = '{}';".format(
        current_timestamp, user_name
    )
    cursor.execute(query)
    connection.commit()

    # users_table = pd.read_csv("users.csv")
    # users_table.loc[users_table["name"]==user_name, "last_time_online"] = current_timestamp
    # users_table.to_csv("users.csv", index=False)


# Window providing functionality to send feedback
def feedback_screen():
    global FEEDBACK_WINDOW
    FEEDBACK_WINDOW = tk.Toplevel(main_window)
    FEEDBACK_WINDOW.title("Edit mood")
    FEEDBACK_WINDOW.geometry("400x300")

    feedback_label = tk.Label(
        FEEDBACK_WINDOW,
        text="Please enter your honest feedback:",
        bg="yellow",
        font=("Calibri", 15),
        anchor="nw",
        justify="left",
        bd=4,
    )
    feedback_label.place(relheight=1, relwidth=1)

    feedback_entry = tk.Text(feedback_label, bg="orange", font=("Calibri", 15), bd=5)
    feedback_entry.place(relx=0, rely=0.2, relheight=0.55, relwidth=1)

    feedback_saving_button = tk.Button(
        feedback_label,
        text="Send feedback",
        bg="grey",
        font=("Calibri", 15),
        command=lambda: send_feedback(feedback_entry.get("1.0", "end-1c")),
    )
    feedback_saving_button.place(relx=0.05, rely=0.8, relheight=0.2, relwidth=0.425)

    feedback_cancelling_button = tk.Button(
        feedback_label,
        text="Cancel",
        bg="grey",
        font=("Calibri", 15),
        command=lambda: close_window(FEEDBACK_WINDOW),
    )
    feedback_cancelling_button.place(relx=0.5, rely=0.8, relheight=0.2, relwidth=0.425)


# Sending the feedback message to the feedback table
def send_feedback(feedback_message):
    current_timestamp = int(time.time())

    # TODO: allow for czech characters in feedback_message, now it throws error
    query = """INSERT INTO feedback (user_name, message, timestamp)
                VALUES ('{}', '{}', '{}');
            """.format(
        USER_NAME, feedback_message, current_timestamp
    )
    cursor.execute(query)
    connection.commit()

    # Closing the feedback window and showing a grateful message
    close_window(FEEDBACK_WINDOW)
    show_message_to_user(
        "Thank you for the feedback!\nWe will analyse your request as soon as possible."
    )


# Defining the main window and its title
main_window = tk.Tk()
main_window.state("zoomed")  # Making the window maximized
main_window.title(TITLE)

# Setting the background image - if the image exists in the current dir
# Having an if-statement not to be dependant on it in the case of .exe file
if os.path.isfile("./background.png"):
    background_image = tk.PhotoImage(file="background.png")
    background_label = tk.Label(main_window, image=background_image)
    background_label.place(x=0, y=0, relwidth=1, relheight=1)


# PROFILE PART
profile_area = tk.Frame(main_window, bg="#42b6f4", bd=5)
profile_area.place(relx=0.05, rely=0.1, relwidth=0.45, relheight=0.15)

name_label = tk.Label(
    profile_area, bg="yellow", font=("Calibri", 15), anchor="nw", justify="left", bd=4
)
name_label.place(rely=0, relheight=0.5, relwidth=0.75)

mood_label = tk.Label(
    profile_area, bg="yellow", font=("Calibri", 15), anchor="nw", justify="left", bd=4
)
mood_label.place(rely=0.5, relheight=0.5, relwidth=0.75)

settings_button = tk.Button(
    profile_area,
    text="Settings",
    bg="grey",
    font=("Calibri", 15),
    command=lambda: show_settings_screen(),
)
settings_button.place(relx=0.75, rely=0, relheight=0.5, relwidth=0.25)

mood_button = tk.Button(
    profile_area,
    text="Edit mood",
    bg="grey",
    font=("Calibri", 15),
    command=lambda: edit_mood_screen(),
)
mood_button.place(relx=0.75, rely=0.5, relheight=0.5, relwidth=0.25)


# FEEDBACK PART
feedback_area = tk.Frame(main_window, bg="yellow", bd=5)
feedback_area.place(relx=0.59, rely=0.05, relwidth=0.1, relheight=0.15)

feedback_button = tk.Button(
    feedback_area,
    text="FEEDBACK",
    bg="blue",
    font=("Calibri", 15),
    command=lambda: feedback_screen(),
)
feedback_button.place(relx=0.01, rely=0.01, relheight=0.98, relwidth=0.98)


# LOGIN/LOGOFF PART
login_area = tk.Frame(main_window, bg="yellow", bd=5)
login_area.place(relx=0.7, rely=0.05, relwidth=0.25, relheight=0.15)

login_button = tk.Button(
    login_area,
    text="LOGIN",
    bg="green",
    font=("Calibri", 15),
    command=lambda: login_screen(),
)
login_button.place(relx=0.01, rely=0.01, relheight=0.98, relwidth=0.48)

logout_button = tk.Button(
    login_area,
    text="LOGOUT",
    bg="red",
    font=("Calibri", 15),
    command=lambda: log_out_from_application(),
)
logout_button.place(relx=0.5, rely=0.01, relheight=0.98, relwidth=0.48)


# MESSAGING PART
messaging_area = tk.Frame(main_window, bg="#42b6f4", bd=10)
messaging_area.place(relx=0.3, rely=0.3, relwidth=0.65, relheight=0.65)

current_contact_label = tk.Label(
    messaging_area,
    text="Current contact - ",
    bg="yellow",
    font=("Calibri", 15),
    justify="right",
)
current_contact_label.place(relx=0, rely=0, relheight=0.09, relwidth=1)

scrollbar = tk.Scrollbar(messaging_area)
scrollbar.place(relx=0.97, rely=0.1, relheight=0.7, relwidth=0.05)

messaging_area_text = tk.Text(
    messaging_area,
    bg="yellow",
    font=("Calibri", 15),
    state="disabled",
    bd=4,
    yscrollcommand=scrollbar.set,
)
messaging_area_text.place(relx=0, rely=0.1, relheight=0.7, relwidth=0.97)

scrollbar.config(command=messaging_area_text.yview)

message_typing_label = tk.Label(
    messaging_area, text="", bg="yellow", font=("Calibri", 15), bd=4, anchor="w"
)
message_typing_label.place(relx=0, rely=0.8, relheight=0.05, relwidth=0.5)

message_displayed_label = tk.Label(
    messaging_area, text="", bg="yellow", font=("Calibri", 15), bd=4, anchor="e"
)
message_displayed_label.place(relx=0.5, rely=0.8, relheight=0.05, relwidth=0.47)

messaging_text = tk.Text(messaging_area, bg="orange", font=("Calibri", 15), bd=5)
messaging_text.place(relx=0, rely=0.85, relheight=0.15, relwidth=0.8)

messaging_button = tk.Button(
    messaging_area,
    text="Send",
    bg="grey",
    font=("Calibri", 20),
    justify="center",
    command=lambda: send_message(
        messaging_text.get("1.0", "end-1c"), CURRENT_CONVERSATION_ID
    ),
)
messaging_button.place(relx=0.8, rely=0.85, relheight=0.15, relwidth=0.2)


# CONTACTS PART
contacts_area = tk.Frame(main_window, bg="#42b6f4", bd=10)
contacts_area.place(relx=0.05, rely=0.3, relwidth=0.2, relheight=0.65)

contact_space_for_buttons = tk.Text(
    contacts_area, bg="yellow", font=("Calibri", 15), bd=4, state="disabled"
)
contact_space_for_buttons.place(relheight=0.9, relwidth=1)

contact_new_button = tk.Button(
    contacts_area,
    text="Add contacts",
    bg="grey",
    font=("Calibri", 15),
    justify="center",
    command=lambda: add_contacts_screen(),
)
contact_new_button.place(relx=0, rely=0.8, relheight=0.1, relwidth=1)

contact_requests_button = tk.Button(
    contacts_area,
    text="Manage requests",
    bg="grey",
    font=("Calibri", 15),
    justify="center",
    command=lambda: manage_contact_requests_screen(),
)
contact_requests_button.place(relx=0, rely=0.9, relheight=0.1, relwidth=1)


# Checking if there is already a directory to store conversations,
#   and if not, create it
if not os.path.exists("Conversations"):
    os.mkdir("Conversations")

# Saving time with no login :)
# log_user_into_application("tt")

# Cause everything to update with the pause of 2 seconds
# Only when there is some user logged in (USER_NAME is not empty)
def update_the_page():
    if USER_NAME != "":
        populate_contacts()
        update_number_of_requests()
        populate_conversation(
            CURRENT_CONVERSATION_ID,
            CURRENTLY_OPENED_CONTACT_NAME,
            CURRENTLY_OPENED_CONTACT_MOOD,
        )
        log_last_time_online(USER_NAME)
    main_window.after(2000, update_the_page)


update_the_page()


main_window.mainloop()
