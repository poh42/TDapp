from db import db

game_has_console_table = db.Table(
    "games_has_consoles",
    db.Column("game_id", db.Integer, db.ForeignKey("games.id"), primary_key=True),
    db.Column("console_id", db.Integer, db.ForeignKey("consoles.id"), primary_key=True),
)
