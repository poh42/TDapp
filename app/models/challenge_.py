from datetime import datetime

from sqlalchemy import text

from db import db
from sqlalchemy.sql import func
from sqlalchemy.orm import aliased
from models.challenge_user import ChallengeUserModel
from models.results_1v1 import Results1v1Model
from models.dispute import DisputeModel
from models.console import ConsoleModel

STATUS_COMPLETED = "COMPLETED"
STATUS_ACCEPTED = "ACCEPTED"
STATUS_PENDING = "PENDING"
STATUS_OPEN = "OPEN"
STATUS_REJECTED = "REJECTED"
STATUS_IN_PROGRESS = "IN_PROGRESS"
STATUS_REPORTING = "REPORTING"
STATUS_DISPUTED = "DISPUTED"
STATUS_SOLVED = "SOLVED"


class ChallengeModel(db.Model):
    __tablename__ = "challenges"
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(45), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey("games.id"), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    buy_in = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
    reward = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
    status = db.Column(db.String(45), nullable=False)
    due_date = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, onupdate=func.now())
    game = db.relationship("GameModel")
    challenge_users = db.relationship(
        "ChallengeUserModel", lazy="dynamic", cascade="all, delete-orphan"
    )
    results_1v1 = db.relationship(
        "Results1v1Model", cascade="all, delete-orphan", uselist=False
    )

    disputes = db.relationship("DisputeModel", cascade="all, delete-orphan")

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def find_user_challenges(cls, user_id, **kwargs):
        """Finds challenges that are related to a user"""
        challenge_users = aliased(cls.challenge_users)
        results_1v1 = aliased(cls.results_1v1)
        query = cls.query.join(challenge_users).filter(
            challenge_users.challenged_id == user_id
        )
        if kwargs.get("upcoming"):
            query = query.filter(cls.date >= datetime.now())
        if kwargs.get("last_results"):
            last_results = int(kwargs.get("last_results", 0))
            query = (
                query.join(results_1v1)
                .order_by(results_1v1.played.desc())
                .limit(last_results)
            )
        query_data = query.all()
        return query_data

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    def user_can_report_challenge(self, user_id):
        """Checks if a user can report a challenge or not"""
        sql = """
        select 1 from challenge_users cu
            where (cu.challenged_id = :user_id OR cu.challenger_id = :user_id) and cu.wager_id = :challenge_id
            and cu.status_challenger not in ('REJECTED', 'FINISHED', 'COMPLETED', 'SOLVED')
            and cu.status_challenged not in ('REJECTED', 'FINISHED', 'COMPLETED', 'SOLVED')
        limit 1
        """
        data = db.engine.execute(
            text(sql), user_id=user_id, challenge_id=self.id
        ).fetchone()
        return data is not None
