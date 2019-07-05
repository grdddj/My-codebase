import os
from twilio.rest import Client

account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
twilio_number = os.environ['TWILIO_NUMBER']
my_number = os.environ['MY_NUMBER']

client = Client(account_sid, auth_token)

text = "Input something sweet (and short)"

message = client.messages.create(
                              body=text,
                              from_=twilio_number,
                              to=my_number
                          )

print(message.sid)
