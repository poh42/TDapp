from db import db
from sqlalchemy.sql import func


class UserChallengeScoresModel(db.Model):
    __tablename__ = "results_1v1"

    challenge_id = db.Column(db.Integer, db.ForeignKey("challenges.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    own_score = db.Column(db.Integer, nullable=False)
    opponent_score = db.Column(db.Integer, nullable=False)
    screenshot = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, onupdate=func.now())

    user = db.relationship("UserModel", foreign_keys=[user_id])
    challenge = db.relationship("ChallengeModel", foreign_keys=[challenge_id])

    @classmethod
    def find_by_challenge_id_user_id(cls, challenge_id, user_id):
        return cls.query\
        .filter_by(challenge_id=challenge_id)\
        .filter_by(user_id=user_id)\
        .first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
