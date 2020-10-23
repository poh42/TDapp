from models.game import GameModel
from models.results_1v1 import Results1v1Model
from models.challenge_ import ChallengeModel
from flask_restful import Resource
from schemas.challenge_ import ChallengeSchema
from flask import request
from datetime import datetime
from sqlalchemy.orm import joinedload

challenge_schema = ChallengeSchema()


class Challenge(Resource):
    @classmethod
    def get(cls, challenge_id):
        challenge = ChallengeModel.find_by_id(challenge_id)
        if not challenge:
            return {"message": "Challenge not found"}, 404
        return {
            "message": "Challenge found",
            "challenge": challenge_schema.dump(challenge),
        }

    @classmethod
    def delete(cls, challenge_id):
        challenge = ChallengeModel.find_by_id(challenge_id)
        if not challenge:
            return {"message": "Challenge not found"}, 404
        challenge.delete_from_db()
        return {"message": "Challenge deleted"}, 200


class ChallengeList(Resource):
    @classmethod
    def get(cls):
        query = ChallengeModel.query.options(joinedload(ChallengeModel.game))
        if request.args.get("upcoming") == "true":
            query = query.filter(ChallengeModel.date >= datetime.now())
        try:
            last_results = int(request.args.get("lastResults", 0))
        except ValueError:
            return {"message": "Invalid lastResults value"}, 400
        if last_results:
            query = (
                query.join(Results1v1Model)
                .order_by(Results1v1Model.played.desc())
                .limit(last_results)
            )
        return {"challenges": challenge_schema.dump(query.all(), many=True)}
