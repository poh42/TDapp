from models.challenge_ import ChallengeModel
from models.confirmation import ConfirmationModel
from models.dispute import DisputeModel
from models.game_has_console import game_has_console_table
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

CALL_OF_DUTY_PHOTO = "https://flashdrive69.s3.amazonaws.com/29b702dcb15472be22798442b42976e8eb2660466b0e5082ce0f29c9e4ae10df.jpeg"
FIFA_PHOTO = "https://flashdrive69.s3.amazonaws.com/c05359bd42284aff325249862573d56a3403aaecba7ff6e97a08ce690ce8e835.jpg"
MLB_PHOTO = "https://flashdrive69.s3.amazonaws.com/f6ad72675c8cf43784b56d2f19ff70a9c4cef2b9c9951ac5413733b3f96fd186.jpg"
NFL_PHOTO = "https://flashdrive69.s3.amazonaws.com/3eef44c2f23474470b273e4f8ddc5e1861a021da86c8c9853f4daf647c368f53.jpg"
NBA_PHOTO = "https://flashdrive69.s3.amazonaws.com/15473dcd5b937b78d64e859181a7dd921ff639227e5939561cdf276a546d977d.jpg"


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


def create_login_user():
    user = UserModel()
    user.email = "asdr@hotmail.com"
    user.password = "1234567"
    user.username = "asdrutest"
    user.firebase_id = "myLbdKL8dFhipvanv4AnIUaJpqd2"
    user.avatar = "https://avatar.com/3"
    user.save()
    return user


def create_dummy_game():
    game = GameModel()
    game.name = "FIFA"
    game.image = FIFA_PHOTO
    game.is_active = True
    game.save_to_db()
    return game


def create_dummy_game_not_active():
    game = GameModel()
    game.name = "Inactive game"
    game.image = "dummy.jpg"
    game.is_active = False
    game.save_to_db()
    return game


def create_rest_of_games(console_id):
    # MLB The show
    mlb = GameModel()
    mlb.name = "MLB The show"
    mlb.image = MLB_PHOTO
    mlb.is_active = True
    mlb.save_to_db()
    create_dummy_console_relationship(console_id, mlb.id)

    # NFL
    nfl = GameModel()
    nfl.name = "NFL"
    nfl.image = NFL_PHOTO
    nfl.is_active = True
    nfl.save_to_db()
    create_dummy_console_relationship(console_id, nfl.id)

    # Call of Duty
    cod = GameModel()
    cod.name = "Call of Duty"
    cod.image = CALL_OF_DUTY_PHOTO
    cod.is_active = True
    cod.save_to_db()
    create_dummy_console_relationship(console_id, cod.id)

    # NBA
    nba = GameModel()
    nba.name = "NBA"
    nba.image = NBA_PHOTO
    nba.is_active = True
    nba.save_to_db()
    create_dummy_console_relationship(console_id, nba.id)


def create_dummy_console():
    console = ConsoleModel()
    console.name = "PS1"
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


def create_dummy_console_relationship(console_id, game_id):
    insert = game_has_console_table.insert().values(
        console_id=console_id, game_id=game_id
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


def create_confirmation_already_confirmed(user_id):
    confirmation = ConfirmationModel(user_id)
    confirmation.confirmed = True
    confirmation.save_to_db()
    return confirmation


def create_dispute(user_id, challenge_id):
    dispute = DisputeModel()
    dispute.user_id = user_id
    dispute.challenge_id = challenge_id
    dispute.status = "OPEN"
    dispute.comments = "TEST"
    dispute.save_to_db()
    return dispute


def create_fixtures():
    user = create_dummy_user()
    user_login = create_login_user()
    second_user = create_second_user()
    game = create_dummy_game()
    game_not_active = create_dummy_game_not_active()
    console = create_dummy_console()
    challenge = create_dummy_challenge(game.id)
    result_1v1 = create_dummy_result(challenge.id, user.id, user.id)
    create_dummy_friendship(user.id, second_user.id)
    create_dummy_friendship(user_login.id, second_user.id)
    user_game = create_dummy_user_game(game.id, second_user.id, console.id)
    transaction = create_dummy_transaction(second_user.id)
    transaction2 = create_dummy_transaction(user_login.id)
    confirmation = create_confirmation_already_confirmed(user_login.id)
    dispute = create_dispute(user_login.id, challenge.id)
    create_rest_of_games(console.id)
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
        "transaction2": transaction2,
        "user_login": user_login,
        "confirmation": confirmation,
        "dispute": dispute,
    }
