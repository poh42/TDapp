from db import db


class ChallengeScreenshot(db.Model):
    __tablename__ = "challenge_screenshots"
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(255), nullable=False)
    approved = db.Column(db.Boolean, default=False)
    challenge_id = db.Column(db.Integer, db.ForeignKey("challenges.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    type = db.Column(db.String(255), nullable=False)
