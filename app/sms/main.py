from datetime import datetime
from models.challenge_user import ChallengeUserModel
from sms.utils_ import send_msg


def get_date_from_string(d):
    return datetime.strptime(d, "%Y-%m-%d %H:%M:%S")


def minutes_between(d1, d2):
    return int(abs((d2 - d1).total_seconds()) / 60)


def send_messages_challenge_users(number, challenge_user, is_challenger):
    user = challenge_user.challenger if is_challenger else challenge_user.challenged
    user_2 = challenge_user.challenged if is_challenger else challenge_user.challenger
    now = datetime.utcnow()
    if number is not None and user is not None and user_2 is not None:
        challenge = challenge_user.challenge
        game = challenge.game
        date_challenge = challenge.date
        minutes = minutes_between(now, date_challenge)
        if date_challenge > now:
            if minutes == 0:
                portion = "begins now"
            elif minutes == 1:
                portion = "begins in a minute"
            else:
                portion = f"begins in {minutes} minutes"
        else:
            portion = "begins now"
        message_text = f"Hello, your challenge with the user {user_2.username} in {game.name} {portion}"
        return send_msg(message_text, number)
    return False


def send_message_challenge_user(challenge_user: ChallengeUserModel):
    modified = False
    if not challenge_user.challenged_sms_sent:
        user = challenge_user.challenged
        if user is not None:
            sms_sent = send_messages_challenge_users(user.phone, challenge_user, False)
            if sms_sent:
                modified = True
                challenge_user.challenged_sms_sent = True
    if not challenge_user.challenger_sms_sent:
        user = challenge_user.challenger
        if user is not None:
            sms_sent = send_messages_challenge_users(user.phone, challenge_user, True)
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
