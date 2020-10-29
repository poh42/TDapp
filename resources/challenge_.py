from marshmallow import ValidationError

from db import db
from decorators import check_token
from models.challenge_user import ChallengeUserModel, STATUS_OPEN
from models.dispute import DisputeModel
from models.game import GameModel
from models.transaction import TransactionModel
from models.results_1v1 import Results1v1Model
from models.challenge_ import ChallengeModel
from flask_restful import Resource
from models.user import UserModel
from schemas.challenge_ import ChallengeSchema
from flask import request, g
from datetime import datetime
from sqlalchemy.orm import joinedload
from sqlalchemy import or_, text
from schemas.challenge_user import ChallengeUserSchema
from schemas.dispute import DisputeSchema
from schemas.results_1v1 import Results1v1Schema

challenge_schema = ChallengeSchema()
challenge_user_schema = ChallengeUserSchema()
results_1v1_schema = Results1v1Schema()
dispute_schema = DisputeSchema()


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

    @classmethod
    def put(cls, challenge_id):
        challenge = ChallengeModel.find_by_id(challenge_id)
        if not challenge:
            return {"message": "Challenge not found"}, 400
        json_data = request.get_json()
        errors = challenge_schema.validate(json_data, partial=True)
        if errors:
            raise ValidationError(errors)
        if json_data.get("type"):
            challenge.type = json_data.get("type")
        if json_data.get("name"):
            challenge.name = json_data.get("name")
        if json_data.get("buy_in"):
            challenge.buy_in = json_data.get("buy_in")
        if json_data.get("reward"):
            challenge.reward = json_data.get("reward")
        if json_data.get("status"):
            challenge.status = json_data.get("status")
        if json_data.get("due_date"):
            challenge.due_date = json_data.get("due_date")
        try:
            challenge.save_to_db()
        except Exception as e:
            print(e)
            return {"message": "There was an error saving the challenge"}, 400
        return (
            {
                "message": "Challenge saved successfully",
                "challenge": challenge_schema.dump(challenge),
            },
            200,
        )


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


class ResultsByUser(Resource):
    @classmethod
    def get(cls, user_id):
        sql = text(
            """
            select
                c.id as challenge_id,
                c."name" as challenge_name,
                g."name" as game_name,
                rv.played,
                rv.score_player_1,
                rv.score_player_2,
                u1.username as user_1_username,
                u2.username as user_2_username
            from
                results_1v1 rv
            inner join challenges c on
                rv.challenge_id = c.id
            inner join users u1 on
                rv.player_1_id = u1.id
            inner join users u2 on
                rv.player_2_id = u2.id
            inner join games g on
                g.id = c.game_id 
            where
                rv.played is not null
                and (rv.player_1_id = :user_id
                or rv.player_2_id = :user_id)
            order by rv.played DESC
            """
        )

        results = db.engine.execute(sql, user_id=user_id).fetchall()
        return {"message": "Results found", "results": [dict(r) for r in results]}


class ChallengePerson(Resource):
    @classmethod
    @check_token
    def post(cls, challenged_id):
        challenge_user: ChallengeUserModel = challenge_user_schema.load(
            request.get_json()
        )
        user = UserModel.find_by_id(challenged_id)
        if not user:
            return {"message": "User not found"}, 400
        current_user = g.claims.get("user_id", None)
        if current_user is None:
            return {"message": "Wrong claims"}, 400
        challenge_user.challenger_id = UserModel.find_by_firebase_id(current_user).id
        challenge_user.challenged_id = challenged_id
        challenge_user.status = STATUS_OPEN
        challenge_user.save_to_db()
        return (
            {
                "challenge_user": challenge_user_schema.dump(challenge_user),
                "message": "User challenged",
            },
            200,
        )


class ChallengeResults(Resource):
    @classmethod
    def get(cls, challenge_id):
        results = Results1v1Model.find_by_challenge_id(challenge_id)
        if not results:
            return {"message": "Results not found"}, 400
        return {"message": "Results found", "results": results_1v1_schema.dump(results)}


class ReportChallenge(Resource):
    @classmethod
    @check_token
    def post(cls, challenge_id):
        json_data = request.get_json()
        dispute: DisputeModel = dispute_schema.load(json_data)
        dispute.challenge_id = challenge_id
        current_user_firebase_id = g.claims.get("user_id", None)
        if current_user_firebase_id is None:
            return {"message": "Wrong claims"}, 400
        dispute.user_id = UserModel.find_by_firebase_id(current_user_firebase_id).id
        dispute.save_to_db()
        return (
            {"message": "Dispute created", "dispute": dispute_schema.dump(dispute)},
            200,
        )
