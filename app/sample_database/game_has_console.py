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
        # FIFA 21
        {"game": games["fifa21"], "console": consoles["playstation"]},
        {"game": games["fifa21"], "console": consoles["xbox"]},
        {"game": games["fifa21"], "console": consoles["pc"]},
        # Mario Kart Deluxe
        {"game": games["mario_kart"], "console": consoles["xbox"]},
        # COD Modern Warfare
        {"game": games["cod_modern_warfare"], "console": consoles["cross-platform"]},
        # PGA 2k21
        {"game": games["pga_2k21"], "console": consoles["xbox"]},
        # COD Cold War
        {"game": games["cod_cold_war"], "console": consoles["cross-platform"]},
        # Madden 21
        {"game": games["madden21"], "console": consoles["xbox"]},
        # Rocket league
        {"game": games["rocket_league"], "console": consoles["pc"]},
    )


def save(games, consoles):
    relationships = get_relationships(games, consoles)
    ret_val = []
    for r in relationships:
        rel = create_relationship(r["game"], r["console"])
        ret_val.append(rel)
    return ret_val
