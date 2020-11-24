from db import db
from sqlalchemy.sql import func


class Results1v1Model(db.Model):
    __tablename__ = "results_1v1"

    challenge_id = db.Column(
        db.Integer, db.ForeignKey("challenges.id"), primary_key=True
    )
    score_player_1 = db.Column(db.Integer, nullable=False)
    score_player_2 = db.Column(db.Integer, nullable=False)
    player_1_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    player_2_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    played = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, onupdate=func.now())
    winner_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    player_1 = db.relationship("UserModel", foreign_keys=[player_1_id])
    player_2 = db.relationship("UserModel", foreign_keys=[player_2_id])
    winner = db.relationship("UserModel", foreign_keys=[winner_id])
    challenge = db.relationship("ChallengeModel")

    @classmethod
    def find_by_challenge_id(cls, challenge_id):
        return cls.query.filter_by(challenge_id=challenge_id).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
