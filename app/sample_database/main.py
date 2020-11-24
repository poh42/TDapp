from sample_database.console import save as save_consoles
from sample_database.game import save as save_games
from sample_database.game_has_console import save as save_game_has_consoles
from sample_database.user import save as save_users
from sample_database.friendship import save as save_friendships
from sample_database.user_game import save as save_user_games
from sample_database.challenge_ import save as save_challenges
from sample_database.challenge_user import save as save_challenge_users
from sample_database.results_1v1 import save as save_results_1v1


def create_fixtures():
    consoles = save_consoles()
    games = save_games()
    game_has_consoles = save_game_has_consoles(games, consoles)
    users = save_users()
    friendships = save_friendships(users)
    user_games = save_user_games(games, users, consoles)
    challenges = save_challenges(games)
    challenge_users = save_challenge_users(challenges, users)
    results_1v1 = save_results_1v1(challenges, users)
    return {
        "consoles": consoles,
        "games": games,
        "game_has_consoles": game_has_consoles,
        "users": users,
        "friendships": friendships,
        "user_games": user_games,
        "challenges": challenges,
        "challenge_users": challenge_users,
        "results_1v1": results_1v1,
    }
