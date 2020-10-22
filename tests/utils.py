from models.challenge_ import ChallengeModel
from models.user import UserModel
from models.game import GameModel

email = "test@topdog.com"
password = "Pa55w0rd"
username = "asdrubal"


def create_dummy_user():
    user = UserModel()
    user.email = email
    user.password = password
    user.username = username
    user.firebase_id = "dummy"
    user.save()
    return user


def create_dummy_game():
    game = GameModel()
    game.name = "FIFA"
    game.image = "dummy.jpg"
    game.save_to_db()
    return game


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
    challenge = create_dummy_challenge(game.id)
    return {"user": user, "game": game, "challenge": challenge}
