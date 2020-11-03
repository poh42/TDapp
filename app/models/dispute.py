from db import db
from sqlalchemy.sql import func

STATUS_OPEN = "OPEN"
STATUS_DECIDED = "DECIDED"


class DisputeModel(db.Model):
    __tablename__ = "disputes"

    id = db.Column(db.Integer, primary_key=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey("challenges.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    comments = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(45), nullable=False, default=STATUS_OPEN)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, onupdate=func.now())

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def get_by_challenge_id(cls, challenge_id):
        return cls.query.filter_by(challenge_id=challenge_id).all()
