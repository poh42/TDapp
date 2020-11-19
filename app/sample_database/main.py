from sample_database.console import save as save_consoles
from sample_database.game import save as save_games
from sample_database.game_has_console import save as save_game_has_consoles


def create_fixtures():
    consoles = save_consoles()
    games = save_games()
    game_has_consoles = save_game_has_consoles(games, consoles)
    return {
        "consoles": consoles,
        "games": games,
        "game_has_consoles": game_has_consoles,
    }
