from db import db


class GameHasUserModel(db.Model):
    __tablename__ = "games_has_users"

    game_id = db.Column(db.Integer, db.ForeignKey("games.id"), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    level = db.Column(db.String(45), nullable=False)
    gamertag = db.Column(db.String(255), nullable=False)
