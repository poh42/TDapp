from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client
import os

# Your Account Sid and Auth Token from twilio.com/console
# and set the environment variables. See http://twil.io/secure
account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
twilio_from_phone = os.environ.get("TWILIO_FROM_PHONE")

if account_sid is None:
    print("Warning: Twilio account sid not set")

if auth_token is None:
    print("Warning: Twilio auth token not set")

if twilio_from_phone is None:
    print("Warning: Twilio from phone not set")

client = Client(account_sid, auth_token)


def send_msg(message_text, number):
    """This is what is used by twilio to send messages"""
    try:
        message = client.messages.create(
            body=message_text,
            from_=twilio_from_phone,
            to=number,
        )
        print("message sent", message.sid)
        return True
    except TwilioRestException:
        return False
