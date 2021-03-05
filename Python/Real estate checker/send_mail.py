import smtplib
import ssl

from config import Config


def send_email(message_text, recipients=Config.recipients):
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(Config.smtp_server, Config.port, context=context) as server:
        server.login(Config.sender_email, Config.password)
        for recipient in recipients:
            print(f"Sending mail to {recipient}")
            whole_message = f"""\
From: {Config.sender_email}
To: {recipient}
Subject: {Config.subject}

{message_text}
"""
            server.sendmail(Config.sender_email, recipient, whole_message)


if __name__ == "__main__":
    send_email(message_text=Config.message_text, recipients=Config.recipients)
