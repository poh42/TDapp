from db import db


class UserGameModel(db.Model):
    __tablename__ = "user_games"
    id = db.Column(db.Integer, primary_key=True)
    console_id = db.Column(db.Integer, db.ForeignKey("consoles.id"))
    game_id = db.Column(db.Integer, db.ForeignKey("games.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    level = db.Column(db.String(45), nullable=False, default="beginner")
    gamertag = db.Column(db.String(255), nullable=False)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
