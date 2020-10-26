from db import db
from sqlalchemy.sql import func


class DisputeModel(db.Model):
    __tablename__ = "disputes"

    id = db.Column(db.Integer, primary_key=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey("challenges.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    comments = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(45), nullable=False)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, onupdate=func.now())
