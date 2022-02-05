"""
This script is checking the availability of investment gin, and sending emails
    to specified recipients whenever it'S availability changes.
"""

import os
import smtplib
import ssl
from typing import List

import requests

from bs4 import BeautifulSoup

page = "https://www.lepsinalada.cz/gin/hvozd-gin/"
class_to_look_for = "availability-value"
recipients = ["recipient@xxx.com", "recipient@yyy.com"]

WORKING_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
current_state_file_name = "current.txt"
current_state_file_location = os.path.join(WORKING_DIRECTORY, current_state_file_name)


def main():
    try:
        response = requests.get(page)
    except:
        print("It was not possible to fetch data from the page {page}")
        exit()

    soup = BeautifulSoup(response.text, "html.parser")

    try:
        availability_text = (
            soup.find(class_=class_to_look_for).get_text().strip()
        )  # type: ignore
    except AttributeError:
        print(f"Class with name {class_to_look_for} does not exist there!")
        exit()

    try:
        with open(current_state_file_location, "r") as file:
            current_state = file.read().strip()
    except FileNotFoundError:
        print("The file is not there yet, filling it with the first availability info.")
        with open(current_state_file_location, "w") as file:
            file.write(availability_text)
    else:
        if availability_text != current_state:
            send_emails(recipients, availability_text)
            with open(current_state_file_location, "w") as file:
                file.write(availability_text)
            print("The value has changed, and the emails were sent!")
        else:
            print("There was no change from the previous run!")

    print(f"Current availability text: {availability_text}")


def send_emails(recipients: List[str], availability_text: str) -> None:
    """
    This function is sending emails to specified email addresses with a new
        update considering the availability of the goods.
    It suffers small problem with python text encoding, which is not able to
        transfer words in czech language, so the text must be encoded into
        bytes, and it does not look the best when receiving the email.
    """
    for recipient in recipients:
        try:
            # Sending the output as an email
            port = 465  # For SSL
            smtp_server = "smtp.gmail.com"
            sender_email = "scraper006@gmail.com"  # Enter your address
            receiver_email = recipient  # Enter receiver address
            password = "+Scraper006+"

            message = f"""\
            Subject: Time to buy!

            Current state of the availability: {availability_text.encode("utf-8")}
            """

            context = ssl.create_default_context()

            with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
                server.login(sender_email, password)
                server.sendmail(sender_email, receiver_email, message)
        except Exception as e:
            print(f"It looks like we could not send the email to {recipient}")
            print(f"Error message: {e}")


if __name__ == "__main__":
    main()
