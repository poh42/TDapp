from db import db
from sqlalchemy.sql import func
from models.game_has_console import game_has_console_table


class ConsoleModel(db.Model):
    __tablename__ = "consoles"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, onupdate=func.now())
    games = db.relationship("GameModel", secondary=game_has_console_table)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
