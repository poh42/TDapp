from datetime import datetime, timedelta

from marshmallow import ValidationError

from db import db
from decorators import check_token
from models.challenge_user import (
    ChallengeUserModel,
    STATUS_OPEN,
    STATUS_READY,
    STATUS_ACCEPTED,
    STATUS_DECLINED,
)
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
from utils.schema import get_fields_user_to_exclude
from decimal import Decimal

challenge_schema = ChallengeSchema()
challenge_user_schema = ChallengeUserSchema()
dispute_schema = DisputeSchema()


class ChallengePost(Resource):
    @classmethod
    @check_token
    def post(cls):
        challenge: ChallengeModel = challenge_schema.load(request.get_json())
        challenge.reward = Decimal(challenge.buy_in) * 2
        challenge.save_to_db()
        current_user = UserModel.find_by_firebase_id(g.claims["uid"])
        # TODO We might want to redefine this if the user challenges directly
        # i.e. putting the challenged_id
        challenge_user = ChallengeUserModel(
            wager_id=challenge.id,
            challenger_id=current_user.id,
        )
        challenge_user.save_to_db()
        return {
            "message": "Challenge created",
            "challenge": challenge_schema.dump(challenge),
            "challenge_user": challenge_user_schema.dump(challenge_user),
        }


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
        challenge_schema = ChallengeSchema(
            only=(
                "id",
                "game.name",
                "console.id",
                "console.name",
                "type",
                "date",
                "buy_in",
                "reward",
                "status",
                "due_date",
                "created_at",
                "updated_at",
                "challenge_users",
                "results_1v1",
            ),
            exclude=(
                "results_1v1.player_1",
                "results_1v1.player_2",
                # challenge users
                # TODO move this to a METHOD
                "challenge_users.challenged.user_games",
                "challenge_users.challenged.is_private",
                "challenge_users.challenged.dob",
                "challenge_users.challenged.is_active",
                "challenge_users.challenged.phone",
                "challenge_users.challenged.range_bet_low",
                "challenge_users.challenged.playing_hours_begin",
                "challenge_users.challenged.playing_hours_end",
                "challenge_users.challenged.range_bet_high",
                "challenge_users.challenged.accepted_terms",
                "challenge_users.challenged.friends",
                "challenge_users.challenged.firebase_id",
                "challenge_users.challenged.created_at",
                "challenge_users.challenged.updated_at",
                "challenge_users.challenged.email",
                # challenger users
                "challenge_users.challenger.user_games",
                "challenge_users.challenger.is_private",
                "challenge_users.challenger.dob",
                "challenge_users.challenger.is_active",
                "challenge_users.challenger.phone",
                "challenge_users.challenger.range_bet_low",
                "challenge_users.challenger.playing_hours_begin",
                "challenge_users.challenger.playing_hours_end",
                "challenge_users.challenger.range_bet_high",
                "challenge_users.challenger.accepted_terms",
                "challenge_users.challenger.friends",
                "challenge_users.challenger.firebase_id",
                "challenge_users.challenger.created_at",
                "challenge_users.challenger.updated_at",
                "challenge_users.challenger.email",
                # winner
                "results_1v1.winner.firebase_id",
                "results_1v1.winner.user_games",
                "results_1v1.winner.is_private",
                "results_1v1.winner.dob",
                "results_1v1.winner.is_active",
                "results_1v1.winner.phone",
                "results_1v1.winner.range_bet_low",
                "results_1v1.winner.playing_hours_begin",
                "results_1v1.winner.playing_hours_end",
                "results_1v1.winner.range_bet_high",
                "results_1v1.winner.accepted_terms",
                "results_1v1.winner.firebase_id",
                "results_1v1.winner.email",
                "results_1v1.winner.created_at",
                "results_1v1.winner.updated_at",
                "results_1v1.winner.friends",
                # games
                "game.consoles",
            ),
        )
        return {"challenges": challenge_schema.dump(query.all(), many=True)}


class ResultsByUser(Resource):
    @classmethod
    def get(cls, user_id):
        sql = text(
            """
            select
                c.id as challenge_id,
                g."name" as game_name,
                rv.played,
                rv.score_player_1,
                rv.score_player_2,
                rv.winner_id,
                u1.username as user_1_username,
                u2.username as user_2_username,
                u1.id as user_1_id,
                u2.id as user_2_id,
                u1.avatar as user_1_avatar,
                u2.avatar as user_2_avatar,
                co.name as console
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
            left join consoles co on
                co.id = c.console_id
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
        fields_to_exclude_winner = get_fields_user_to_exclude(
            "winner",
            additional=(
                "friends",
                "avatar",
                "user_games",
                "username",
                "created_at",
                "updated_at",
                "accepted_terms",
                "email",
                "is_active",
                "is_private",
            ),
        )
        results_1v1_schema = Results1v1Schema(
            exclude=fields_to_exclude_winner + ("player_1.friends", "player_2.friends")
        )
        if not results:
            return {"message": "Results not found"}, 400
        return {"message": "Results found", "results": results_1v1_schema.dump(results)}


class ReportChallenge(Resource):
    @classmethod
    @check_token
    def post(cls, challenge_id):
        challenge: ChallengeModel = ChallengeModel.find_by_id(challenge_id)
        if challenge is None:
            return {"message": "Challenge not found"}, 400
        current_user_firebase_id = g.claims.get("user_id", None)
        if current_user_firebase_id is None:
            return {"message": "Wrong claims"}, 400
        user = UserModel.find_by_firebase_id(current_user_firebase_id)
        if not challenge.user_can_report_challenge(user.id):
            return {"message": "This user cannot report this challenge"}, 400
        json_data = request.get_json()
        dispute: DisputeModel = dispute_schema.load(json_data)
        dispute.challenge_id = challenge_id
        dispute.user_id = user.id
        dispute.save_to_db()
        return (
            {"message": "Dispute created", "dispute": dispute_schema.dump(dispute)},
            200,
        )


class GetDisputes(Resource):
    # TODO maybe marge this with the report challenge endpoint
    @classmethod
    @check_token
    def get(cls, challenge_id):
        disputes = DisputeModel.get_by_challenge_id(challenge_id)
        return {"disputes": dispute_schema.dump(disputes, many=True)}


class AcceptChallenge(Resource):
    @classmethod
    @check_token
    def post(cls, challenge_user_id):
        current_user: UserModel = UserModel.find_by_firebase_id(g.claims["user_id"])
        challenge_user: ChallengeUserModel = ChallengeUserModel.find_by_id(
            challenge_user_id
        )
        if challenge_user is None:
            return {"message": "Challenge user not found"}, 400
        if challenge_user.accepted:
            return {"message": "Challenge already accepted"}, 400
        if not challenge_user.open:
            return {"message": "Challenge cannot be accepted"}, 400
        if current_user.id != challenge_user.challenged_id:
            return {"message": "Cannot accept challenge from a different user"}, 400
        challenge_user.status_challenged = STATUS_ACCEPTED
        challenge_user.save_to_db()
        return {"message": "Challenge accepted"}, 200


class DeclineChallenge(Resource):
    @classmethod
    @check_token
    def post(cls, challenge_user_id):
        current_user: UserModel = UserModel.find_by_firebase_id(g.claims["user_id"])
        challenge_user: ChallengeUserModel = ChallengeUserModel.find_by_id(
            challenge_user_id
        )
        if challenge_user is None:
            return {"message": "Challenge user not found"}, 400
        if challenge_user.declined:
            return {"message": "Challenge already declined"}, 400
        if not challenge_user.open:
            return {"message": "Challenge cannot be declined"}, 400
        if current_user.id != challenge_user.challenged_id:
            return {"message": "Cannot decline challenge from a different user"}, 400
        challenge_user.status_challenged = STATUS_DECLINED
        challenge_user.save_to_db()
        return {"message": "Challenge declined"}, 200


class ChallengesByUser(Resource):
    @classmethod
    @check_token
    def get(cls, user_id):
        kwargs = dict()
        if request.args.get("lastResults", type=int):
            kwargs["last_results"] = request.args.get("lastResults")
        if request.args.get("upcoming"):
            kwargs["upcoming"] = True
        user = UserModel.find_by_id(user_id)
        current_user = UserModel.find_by_firebase_id(g.claims["uid"])
        if user is None:
            return {"message": "User not found"}, 400
        # Remark: We prevent here that the current user appears is unreachable if its property
        # is_private is set to True
        if (
            not g.claims.get("admin")
            and user.is_private
            and current_user.id != user.id
            and not user.is_friend_of_user(current_user.id)
        ):
            return {"message": "User challenges for this user are private"}, 400
        challenges = ChallengeModel.find_user_challenges(user_id, **kwargs)
        challenge_schema = ChallengeSchema(
            only=(
                "id",
                "game",
                "console.name",
                "console.id",
                "game.consoles",
                "type",
                "date",
                "buy_in",
                "reward",
                "status",
                "due_date",
                "created_at",
                "updated_at",
                "challenge_users",
                "challenge_users.challenged.avatar",
                "challenge_users.challenged.user_games",
                "challenge_users.challenged.username",
                "challenge_users.challenged.id",
                "challenge_users.challenged.last_name",
                "challenge_users.challenged.name",
                "challenge_users.challenger.avatar",
                "challenge_users.challenger.user_games",
                "challenge_users.challenger.username",
                "challenge_users.challenger.id",
                "challenge_users.challenger.last_name",
                "challenge_users.challenger.name",
                "results_1v1.winner.avatar",
                "results_1v1.winner.user_games",
                "results_1v1.winner.username",
                "results_1v1.winner.id",
                "results_1v1.winner.last_name",
                "results_1v1.winner.name",
            ),
            exclude=(
                "results_1v1.player_1",
                "results_1v1.player_2",
                # challenge users
                "challenge_users.challenged.is_private",
                "challenge_users.challenged.dob",
                "challenge_users.challenged.is_active",
                "challenge_users.challenged.phone",
                "challenge_users.challenged.range_bet_low",
                "challenge_users.challenged.playing_hours_begin",
                "challenge_users.challenged.playing_hours_end",
                "challenge_users.challenged.range_bet_high",
                "challenge_users.challenged.accepted_terms",
                # winner
                "results_1v1.winner.firebase_id",
                "results_1v1.winner.user_games",
                "results_1v1.winner.is_private",
                "results_1v1.winner.dob",
                "results_1v1.winner.is_active",
                "results_1v1.winner.phone",
                "results_1v1.winner.range_bet_low",
                "results_1v1.winner.playing_hours_begin",
                "results_1v1.winner.playing_hours_end",
                "results_1v1.winner.range_bet_high",
                "results_1v1.winner.accepted_terms",
                "results_1v1.winner.firebase_id",
            ),
        )
        return {"challenges": challenge_schema.dump(challenges, many=True)}, 200


class DirectChallenges(Resource):
    @classmethod
    @check_token
    def get(cls):
        current_user = UserModel.find_by_firebase_id(g.claims["uid"])
        challenges = ChallengeModel.get_direct_challenges(current_user.id)
        challenge_schema = ChallengeSchema(
            only=(
                "id",
                "game",
                "game.consoles",
                "type",
                "date",
                "buy_in",
                "reward",
                "status",
                "due_date",
                "created_at",
                "updated_at",
                "challenge_users",
                "challenge_users.challenged.avatar",
                "challenge_users.challenged.user_games",
                "challenge_users.challenged.username",
                "challenge_users.challenged.id",
                "challenge_users.challenged.last_name",
                "challenge_users.challenged.name",
                "challenge_users.challenger.avatar",
                "challenge_users.challenger.user_games",
                "challenge_users.challenger.username",
                "challenge_users.challenger.id",
                "challenge_users.challenger.last_name",
                "challenge_users.challenger.name",
                "results_1v1.winner.avatar",
                "results_1v1.winner.user_games",
                "results_1v1.winner.username",
                "results_1v1.winner.id",
                "results_1v1.winner.last_name",
                "results_1v1.winner.name",
            ),
            exclude=(
                "results_1v1.player_1",
                "results_1v1.player_2",
                # challenge users
                "challenge_users.challenged.is_private",
                "challenge_users.challenged.dob",
                "challenge_users.challenged.is_active",
                "challenge_users.challenged.phone",
                "challenge_users.challenged.range_bet_low",
                "challenge_users.challenged.playing_hours_begin",
                "challenge_users.challenged.playing_hours_end",
                "challenge_users.challenged.range_bet_high",
                "challenge_users.challenged.accepted_terms",
                # winner
                "results_1v1.winner.firebase_id",
                "results_1v1.winner.user_games",
                "results_1v1.winner.is_private",
                "results_1v1.winner.dob",
                "results_1v1.winner.is_active",
                "results_1v1.winner.phone",
                "results_1v1.winner.range_bet_low",
                "results_1v1.winner.playing_hours_begin",
                "results_1v1.winner.playing_hours_end",
                "results_1v1.winner.range_bet_high",
                "results_1v1.winner.accepted_terms",
                "results_1v1.winner.firebase_id",
            ),
        )
        return {"challenges": challenge_schema.dump(challenges, many=True)}, 200


class ChallengeStatusUpdate(Resource):
    @classmethod
    def put(cls, challenge_id):
        now = datetime.now()
        challenge = ChallengeModel.find_by_id(challenge_id)
        if not challenge:
            return {"message": "Challenge not found"}, 404
        current_user = UserModel.find_by_firebase_id(g.claims["uid"])
        challenge_users = ChallengeUserModel.query.filter_by(
            wager_id=challenge.id
        ).first()
        user_belongs_challenge = (
            current_user.id == challenge_users.challenger_id
            or current_user.id == challenge_users.challenged_id
        )
        challenge_users_same_status = (
            challenge_users.status_challenger == challenge_users.status_challenged
        )
        if user_belongs_challenge:
            if challenge_users_same_status:
                challenge.status = challenge_users.status_challenger
                try:
                    now_less_150_sec = now - timedelta(seconds=150)
                    now_plus_150_sec = now + timedelta(seconds=150)
                    if (
                        challenge_users.status_challenged == STATUS_READY
                        and not now_less_150_sec <= challenge.date <= now_plus_150_sec
                    ):
                        return {"message": "Incorrect transition for challenge"}, 403
                    challenge.save_to_db()
                except Exception as e:
                    print(e)
                    return {"message": "There was an error saving the challenge"}, 400
                return (
                    {
                        "message": "Challenge updated successfully",
                        "challenge": challenge_schema.dump(challenge),
                    },
                    200,
                )
            else:
                return {"message": "Incorrect transition for challenge"}, 403
        else:
            return {"message": "User does not belong to challenge"}, 403
