from models.challenge_user import ChallengeUserModel


def send_sms(number):
    print("sending sms", number)
    if number is not None:
        print("message sent")
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
