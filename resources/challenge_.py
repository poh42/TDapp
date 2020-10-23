from models.game import GameModel
from models.challenge_ import ChallengeModel
from flask_restful import Resource
from schemas.challenge_ import ChallengeSchema
from flask import request
from datetime import datetime

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
        query = ChallengeModel.query
        print(request.args)
        if request.args.get("upcoming") == "true":
            query = query.filter(ChallengeModel.date >= datetime.now())

        return {"challenges": challenge_schema.dump(query.all(), many=True)}
