from models.challenge_user import ChallengeUserModel
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

print(account_sid, auth_token, twilio_from_phone)

client = Client(account_sid, auth_token)


def send_sms(number):
    print("sending sms", number)
    if number is not None:
        message = client.messages.create(
            body="Hola mundo",
            from_=twilio_from_phone,
            to=number,
        )
        print("message sent", message.sid)
        return True
    return False


def send_message_challenge_user(challenge_user: ChallengeUserModel):
    modified = False
    if not challenge_user.challenged_sms_sent:
        user = challenge_user.challenged
        if user is not None:
            sms_sent = send_sms(user.phone)
            if sms_sent:
                modified = True
                challenge_user.challenged_sms_sent = True
    if not challenge_user.challenger_sms_sent:
        user = challenge_user.challenger
        if user is not None:
            sms_sent = send_sms(user.phone)
            if sms_sent:
                modified = True
                challenge_user.challenger_sms_sent = True
    if modified:
        challenge_user.save_to_db()


"""
Aquí tendríamos que hacer el esqueleto de twilio, 
vamos a crear un comando de flask que va a tener dos banderas 
que van a significar si se han mandado para el challenger y challenged. 
"""


def send_messages():
    challenges_that_need_sms = ChallengeUserModel.find_all_that_need_sms()
    for challenge_user in challenges_that_need_sms:
        send_message_challenge_user(challenge_user)
