from models.challenge_ import ChallengeModel
from models.transaction import TransactionModel
from models.user import UserModel
from models.game import GameModel
from models.console import ConsoleModel
from models.results_1v1 import Results1v1Model
from models.friendship import friendship_table
from models.user_game import UserGameModel
from datetime import datetime
from db import db


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


def create_second_user():
    user = UserModel()
    user.email = "test@example.com"
    user.password = "1234567"
    user.username = "user2"
    user.firebase_id = "dummy_2"
    user.avatar = "https://avatar.com/2"
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


def create_dummy_result(challenge_id, user1_id, user2_id):
    result_1v1 = Results1v1Model()
    result_1v1.challenge_id = challenge_id
    result_1v1.player_1_id = user1_id
    result_1v1.player_2_id = user2_id
    result_1v1.score_player_1 = 1
    result_1v1.score_player_2 = 0
    result_1v1.played = datetime(2019, 10, 1)
    result_1v1.save_to_db()
    return result_1v1


def create_dummy_friendship(follower_id, followed_id):
    insert = friendship_table.insert().values(
        follower_id=follower_id, followed_id=followed_id
    )
    db.engine.execute(insert)


def create_dummy_user_game(game_id, user_id, console_id):
    user_game = UserGameModel()
    user_game.game_id = game_id
    user_game.user_id = user_id
    user_game.console_id = console_id
    user_game.level = "dummy"
    user_game.gamertag = "dummy"
    user_game.save_to_db()
    return user_game


def create_dummy_transaction(user_id):
    transaction = TransactionModel()
    transaction.previous_credit_total = 0
    transaction.credit_change = 10
    transaction.credit_total = 10
    transaction.user_id = user_id
    transaction.type = "ADD"
    transaction.save_to_db()
    return transaction


def create_fixtures():
    user = create_dummy_user()
    second_user = create_second_user()
    game = create_dummy_game()
    game_not_active = create_dummy_game_not_active()
    console = create_dummy_console()
    challenge = create_dummy_challenge(game.id)
    result_1v1 = create_dummy_result(challenge.id, user.id, user.id)
    create_dummy_friendship(user.id, second_user.id)
    user_game = create_dummy_user_game(game.id, second_user.id, console.id)
    transaction = create_dummy_transaction(second_user.id)
    return {
        "user": user,
        "second_user": second_user,
        "game": game,
        "challenge": challenge,
        "game_not_active": game_not_active,
        "console": console,
        "result_1v1": result_1v1,
        "friendship": {"follower_id": user.id, "followed_id": second_user.id},
        "user_game": user_game,
        "transaction": transaction,
    }
