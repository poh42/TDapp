from models.challenge_ import ChallengeModel
from models.user import UserModel
from models.game import GameModel
from models.console import ConsoleModel

email = "test@topdog.com"
password = "Pa55w0rd"
username = "asdrubal"
avatar = "https://avatar.com/1"


def create_dummy_user():
    user = UserModel()
    user.email = email
    user.password = password
    user.username = username
    user.firebase_id = "dummy"
    user.avatar = avatar
    user.save()
    return user


def create_dummy_game():
    game = GameModel()
    game.name = "FIFA"
    game.image = "dummy.jpg"
    game.is_active = True
    game.save_to_db()
    return game


def create_dummy_game_not_active():
    game = GameModel()
    game.name = "Call of duty"
    game.image = "dummy.jpg"
    game.is_active = False
    game.save_to_db()
    return game


def create_dummy_console():
    console = ConsoleModel()
    console.name = "PS Vita"
    console.save_to_db()
    return console


def create_dummy_challenge(game_id):
    challenge = ChallengeModel()
    challenge.type = "1v1"
    challenge.name = "Challenge"
    challenge.game_id = game_id
    challenge.date = "2019-01-01 15:00:00"
    challenge.due_date = "2019-01-01 15:00:00"
    challenge.buy_in = "10"
    challenge.reward = "100"
    challenge.status = "BEGIN"  # TODO Change this to a more explanatory value
    challenge.save_to_db()
    return challenge


def create_fixtures():
    user = create_dummy_user()
    game = create_dummy_game()
    game_not_active = create_dummy_game_not_active()
    console = create_dummy_console()
    challenge = create_dummy_challenge(game.id)
    return {
        "user": user,
        "game": game,
        "challenge": challenge,
        "game_not_active": game_not_active,
        "console": console,
    }
