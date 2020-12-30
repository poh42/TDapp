from db import db
from sqlalchemy.sql import func


class UserPhotoModel(db.Model):
    __tablename__ = "user_photos"

    id = db.Column(db.Integer, primary_key=True)
    approved = db.Column(db.Boolean, default=False)
    url = db.Column(db.String(255), nullable=False)
    #: Can be avatar or photo_id (For verification purposes)
    type = db.Column(db.String(45), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, onupdate=func.now())

    @classmethod
    def find_by_id(cls, _id) -> "UserPhotoModel":
        return cls.query.filter_by(id=_id).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
