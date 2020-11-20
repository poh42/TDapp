from sample_database.console import save as save_consoles
from sample_database.game import save as save_games
from sample_database.game_has_console import save as save_game_has_consoles
from sample_database.user import save as save_users


def create_fixtures():
    consoles = save_consoles()
    games = save_games()
    game_has_consoles = save_game_has_consoles(games, consoles)
    users = save_users()
    return {
        "consoles": consoles,
        "games": games,
        "game_has_consoles": game_has_consoles,
        "users": users,
    }
