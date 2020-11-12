from sqlalchemy import func

from db import db

STATUS_PENDING = "PENDING"
STATUS_ACCEPTED = "ACCEPTED"
STATUS_REJECTED = "REJECTED"


class InviteModel(db.Model):
    __tablename__ = "invites"

    id = db.Column(db.Integer, primary_key=True)
    user_inviting_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user_invited_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    status = db.Column(db.String(16), nullable=False, default=STATUS_PENDING)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, onupdate=func.now())

    user_inviting = db.relationship("UserModel", foreign_keys=[user_inviting_id])
    user_invited = db.relationship("UserModel", foreign_keys=[user_invited_id])

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()

    @property
    def pending(self):
        return self.status == STATUS_PENDING

    @property
    def accepted(self):
        return self.status == STATUS_ACCEPTED

    @property
    def rejected(self):
        return self.status == STATUS_REJECTED

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def is_already_invited(cls, user_inviting_id, user_invited_id):
        """Checks if the user inviting has already invited another user"""
        return (
            cls.query.filter_by(
                user_inviting_id=user_inviting_id,
                user_invited_id=user_invited_id,
                status=STATUS_PENDING,
            ).first()
            is not None
        )

    def reject(self):
        """Sets status of invite to rejected"""
        self.status = STATUS_REJECTED

    def accept(self):
        """Sets status of invite to accepted"""
        self.status = STATUS_ACCEPTED
