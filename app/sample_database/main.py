from sample_database.console import save as save_consoles
from sample_database.game import save as save_games


def create_fixtures():
    consoles = save_consoles()
    games = save_games()
    return {"consoles": consoles, "games": games}
