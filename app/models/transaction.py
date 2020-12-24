from sqlalchemy import func

from db import db

TYPE_ADD = "ADD"
TYPE_SUBSTRACTION = "SUBSTRACTION"


class TransactionModel(db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)
    previous_credit_total = db.Column(
        db.Numeric(precision=10, scale=2), default=0, nullable=False
    )
    credit_change = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
    credit_total = db.Column(
        db.Numeric(precision=10, scale=2), default=0, nullable=False
    )
    challenge_id = db.Column(db.Integer, db.ForeignKey("challenges.id"), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    type = db.Column(db.String(60), nullable=False)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, onupdate=func.now())

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_by_user_id(cls, _id):
        max_transaction_id = db.session.query(func.max(cls.id)).filter_by(user_id=_id)
        return cls.query.filter_by(id=max_transaction_id).first()
