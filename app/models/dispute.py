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

    challenge = db.relationship("ChallengeModel", uselist=False)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def get_by_challenge_id(cls, challenge_id):
        return cls.query.filter_by(challenge_id=challenge_id).all()

    @classmethod
    def get_all_disputes(cls, kwargs):
        print(kwargs)
        query = cls.query
        status = kwargs.get("status", None)
        if status:
            query = query.filter_by(status=status)
        return query.paginate(kwargs.get("page", 1, type=int), 2)

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()
