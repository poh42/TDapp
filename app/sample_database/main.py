from sample_database.console import save as save_consoles
from sample_database.game import save as save_games
from sample_database.game_has_console import save as save_game_has_consoles
from sample_database.user import save as save_users
from sample_database.friendship import save as save_friendships
from sample_database.user_game import save as save_user_games
from sample_database.challenge_ import save as save_challenges


def create_fixtures():
    consoles = save_consoles()
    games = save_games()
    game_has_consoles = save_game_has_consoles(games, consoles)
    users = save_users()
    friendships = save_friendships(users)
    user_games = save_user_games(games, users, consoles)
    challenges = save_challenges(games)
    return {
        "consoles": consoles,
        "games": games,
        "game_has_consoles": game_has_consoles,
        "users": users,
        "friendships": friendships,
        "user_games": user_games,
        "challenges": challenges,
    }
