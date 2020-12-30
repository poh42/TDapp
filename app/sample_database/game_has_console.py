from models.game_has_console import game_has_console_table
from db import db


def create_relationship(game, console):
    game_id = game.id
    console_id = console.id
    insert = game_has_console_table.insert().values(
        game_id=game_id, console_id=console_id
    )
    db.engine.execute(insert)
    return {"game_id": game_id, "console_id": console_id}


def get_relationships(games, consoles):
    return (
        # FIFA 20
        {"game": games["fifa20"], "console": consoles["playstation"]},
        {"game": games["fifa20"], "console": consoles["xbox"]},
        {"game": games["fifa20"], "console": consoles["pc"]},
        {"game": games["fifa20"], "console": consoles["nintendo-switch"]},
        # FIFA 21
        {"game": games["fifa21"], "console": consoles["playstation"]},
        {"game": games["fifa21"], "console": consoles["xbox"]},
        {"game": games["fifa21"], "console": consoles["pc"]},
        {"game": games["fifa21"], "console": consoles["nintendo-switch"]},
        # Mario Kart Deluxe
        {"game": games["mario_kart"], "console": consoles["nintendo-switch"]},
        # COD Modern Warfare
        {"game": games["cod_modern_warfare"], "console": consoles["cross-platform"]},
        {"game": games["cod_modern_warfare"], "console": consoles["playstation"]},
        {"game": games["cod_modern_warfare"], "console": consoles["xbox"]},
        {"game": games["cod_modern_warfare"], "console": consoles["pc"]},
        # PGA 2k21
        {"game": games["pga_2k21"], "console": consoles["xbox"]},
        {"game": games["pga_2k21"], "console": consoles["playstation"]},
        {"game": games["pga_2k21"], "console": consoles["pc"]},
        {"game": games["pga_2k21"], "console": consoles["nintendo-switch"]},
        # COD Cold War
        {"game": games["cod_cold_war"], "console": consoles["cross-platform"]},
        {"game": games["cod_cold_war"], "console": consoles["playstation"]},
        {"game": games["cod_cold_war"], "console": consoles["xbox"]},
        {"game": games["cod_cold_war"], "console": consoles["pc"]},
        # Madden 20
        {"game": games["madden20"], "console": consoles["xbox"]},
        {"game": games["madden20"], "console": consoles["playstation"]},
        {"game": games["madden20"], "console": consoles["pc"]},
        # Madden 21
        {"game": games["madden21"], "console": consoles["xbox"]},
        {"game": games["madden21"], "console": consoles["playstation"]},
        {"game": games["madden21"], "console": consoles["pc"]},
        {"game": games["madden21"], "console": consoles["nintendo-switch"]},
        # MLB The Show
        {"game": games["mlb_20"], "console": consoles["playstation"]},
        # NBA 2k20
        {"game": games["nba_2k20"], "console": consoles["pc"]},
        {"game": games["nba_2k20"], "console": consoles["xbox"]},
        {"game": games["nba_2k20"], "console": consoles["playstation"]},
        {"game": games["nba_2k20"], "console": consoles["nintendo-switch"]},
        # NBA 2k21
        {"game": games["nba_2k21"], "console": consoles["pc"]},
        {"game": games["nba_2k21"], "console": consoles["xbox"]},
        {"game": games["nba_2k21"], "console": consoles["playstation"]},
        {"game": games["nba_2k21"], "console": consoles["nintendo-switch"]},
        # NHL 20
        {"game": games["nhl_20"], "console": consoles["xbox"]},
        {"game": games["nhl_20"], "console": consoles["playstation"]},
        # NHL 21
        {"game": games["nhl_21"], "console": consoles["xbox"]},
        {"game": games["nhl_21"], "console": consoles["playstation"]},
        # Rocket league
        {"game": games["rocket_league"], "console": consoles["pc"]},
        {"game": games["rocket_league"], "console": consoles["xbox"]},
        {"game": games["rocket_league"], "console": consoles["playstation"]},
        {"game": games["rocket_league"], "console": consoles["nintendo-switch"]},
        {"game": games["rocket_league"], "console": consoles["cross-platform"]},
        # Smash Bros
        {"game": games["smash_bros"], "console": consoles["nintendo-switch"]},
    )


def save(games, consoles):
    relationships = get_relationships(games, consoles)
    ret_val = []
    for r in relationships:
        rel = create_relationship(r["game"], r["console"])
        ret_val.append(rel)
    return ret_val
