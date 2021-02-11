import traceback
from datetime import datetime, timedelta

from marshmallow import ValidationError

from db import db
from decorators import check_token, check_is_admin
from models.user_challenge_scores import UserChallengeScoresModel
from models.challenge_user import (
    ChallengeUserModel,
    STATUS_OPEN,
    STATUS_PENDING,
    STATUS_ACCEPTED,
    STATUS_DECLINED,
    STATUS_READY,
    STATUS_STARTED,
    STATUS_FINISHED,
    STATUS_COMPLETED,
    STATUS_DISPUTED,
    STATUS_SOLVED,
)
from models.dispute import (
    DisputeModel,
    STATUS_OPEN as DISPUTE_STATUS_OPEN,
    STATUS_SOLVED as DISPUTE_STATUS_SOLVED,
)
from models.game import GameModel
from models.transaction import TransactionModel, TYPE_ADD, TYPE_SUBSTRACTION
from models.results_1v1 import Results1v1Model
from models.challenge_ import (
    ChallengeModel,
    STATUS_OPEN,
    STATUS_PENDING,
    STATUS_REJECTED,
    STATUS_ACCEPTED,
    STATUS_READY,
    STATUS_IN_PROGRESS,
    STATUS_REPORTING,
    STATUS_COMPLETED,
    STATUS_DISPUTED as CHALLENGE_STATUS_DISPUTED,
    STATUS_SOLVED,
)
from flask_restful import Resource
from models.user import UserModel
from schemas.challenge_ import ChallengeSchema
from flask import request, g
from datetime import datetime
from sqlalchemy.orm import joinedload
from sqlalchemy import or_, text
from schemas.challenge_user import ChallengeUserSchema
from schemas.user_challenge_score import UserChallengeScoreSchema
from schemas.dispute import DisputeSchema, DisputeAdminSchema, SettleDisputeSchema
from schemas.results_1v1 import Results1v1Schema
from utils.schema import get_fields_user_to_exclude
from decimal import Decimal

from utils.validation import has_game_console

challenge_schema = ChallengeSchema()
user_challenge_score_schema = UserChallengeScoreSchema()
challenge_user_schema = ChallengeUserSchema()
dispute_schema = DisputeSchema()

_USERS_STATUS_FLOW = {
    # [valid status 1, valid status 2, next status, valid challenge status]
    STATUS_OPEN: [
        STATUS_OPEN,
        (STATUS_ACCEPTED, STATUS_READY),
        STATUS_READY,
        STATUS_ACCEPTED,
    ],
    STATUS_ACCEPTED: [
        (STATUS_OPEN, STATUS_READY),
        STATUS_ACCEPTED,
        STATUS_READY,
        STATUS_ACCEPTED,
    ],
    STATUS_READY: [
        (STATUS_OPEN, STATUS_READY, STATUS_STARTED),
        (STATUS_ACCEPTED, STATUS_READY, STATUS_STARTED),
        STATUS_STARTED,
        STATUS_READY,
    ],
    STATUS_STARTED: [
        (STATUS_STARTED, STATUS_READY, STATUS_FINISHED),
        (STATUS_STARTED, STATUS_READY, STATUS_FINISHED),
        STATUS_FINISHED,
        STATUS_STARTED,
    ],
    STATUS_FINISHED: [
        (STATUS_FINISHED, STATUS_STARTED, STATUS_COMPLETED),
        (STATUS_FINISHED, STATUS_STARTED, STATUS_COMPLETED),
        STATUS_COMPLETED,
        STATUS_FINISHED,
    ],
    STATUS_COMPLETED: [
        (STATUS_COMPLETED),
        (STATUS_COMPLETED),
        STATUS_DISPUTED,
        STATUS_COMPLETED,
    ],
}


class ChallengePost(Resource):
    @classmethod
    @check_token
    def post(cls):
        json_data = request.get_json()
        challenged_id = json_data.pop("challenged_id", None)
        current_user = UserModel.find_by_firebase_id(g.claims["uid"])
        transaction = TransactionModel.find_by_user_id(current_user.id)
        challenge: ChallengeModel = challenge_schema.load(json_data)
        if transaction is None or challenge.buy_in > transaction.credit_total:
            return {"message": "Not enough credits"}, 403
        if not has_game_console(challenge.game_id, challenge.console_id):
            return {"message": "User game console relation not matching"}, 400
        if not current_user.has_user_game(challenge.game_id, challenge.console_id):
            return {"message": "User/game not in user games"}, 400
        challenge.is_direct = False
        challenge.status = STATUS_OPEN
        if challenged_id is not None:
            can_challenge_user, error_message = current_user.can_challenge_user(
                challenged_id
            )
            if not can_challenge_user:
                return {"message": error_message}, 400
            challenge.is_direct = True
            challenge.status = STATUS_PENDING
            challenged = UserModel.find_by_id(challenged_id)
            # Note, in here we don't check if the challenged is None
            # Because we already do so in can_challenge_user call
            if not challenged.has_user_game(challenge.game_id, challenge.console_id):
                return {
                    "message": "Challengee doesn't have that user game pair registered"
                }, 400
        challenge.reward = Decimal(challenge.buy_in) * 2
        challenge.due_date = challenge.date + timedelta(minutes=5)
        challenge.save_to_db()
        challenge_user_args = {
            "wager_id": challenge.id,
            "challenger_id": current_user.id,
            "status_challenger": STATUS_OPEN,
            "status_challenged": STATUS_PENDING,
        }
        if challenged_id is not None:
            challenge_user_args["challenged_id"] = challenged_id
        challenge_user = ChallengeUserModel(**challenge_user_args)
        challenge_user.save_to_db()
        challenge_dump_schema = ChallengeSchema(
            only=(
                "buy_in",
                "status",
                "game_id",
                "id",
                "challenge_users.created_at",
                "challenge_users.challenger.username",
                "challenge_users.challenged.username",
                "reward",
                "date",
                "due_date",
                "console.name",
                "console.id",
                "type",
                "game.id",
                "game.name",
            )
        )

        new_transaction = TransactionModel()
        new_transaction.previous_credit_total = transaction.credit_total
        new_transaction.credit_change = challenge.buy_in
        new_transaction.credit_total = transaction.credit_total - challenge.buy_in
        new_transaction.challenge_id = challenge.id
        new_transaction.user_id = current_user.id
        new_transaction.type = TYPE_SUBSTRACTION
        new_transaction.save_to_db()

        return {
            "message": "Challenge created",
            "challenge": challenge_dump_schema.dump(challenge),
        }


class Challenge(Resource):
    @classmethod
    def get(cls, challenge_id):
        challenge = ChallengeModel.find_by_id(challenge_id)
        if not challenge:
            return {"message": "Challenge not found"}, 404
        challenge_schema = ChallengeSchema(
            only=(
                "id",
                "console.id",
                "console.name",
                "game",
                "game.id",
                "game.name",
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
                "challenge_users.challenged.username",
                "challenge_users.challenged.id",
                "challenge_users.challenged.last_name",
                "challenge_users.challenged.name",
                "challenge_users.challenger.avatar",
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
        query = (
            ChallengeModel.query.options(joinedload(ChallengeModel.game))
            .filter(ChallengeModel.is_direct is not True)
            .order_by(ChallengeModel.date.asc())
        )
        if request.args.get("upcoming") == "true":
            query = query.filter(ChallengeModel.date >= datetime.utcnow()).order_by(
                ChallengeModel.date.asc()
            )
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
                "game.id",
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
                c.reward as reward,
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


class ChallengeResults(Resource):
    @classmethod
    def get(cls, challenge_id):
        results = Results1v1Model.find_by_challenge_id(challenge_id)
        results_1v1_schema = Results1v1Schema(
            only=(
                "score_player_1",
                "score_player_2",
                "winner.id",
                "winner.name",
                "winner.last_name",
                "challenge.reward",
                "challenge.console.id",
                "challenge.console.name",
                "challenge.game.id",
                "challenge.game.name",
                "player_1.name",
                "player_1.last_name",
                "player_1.id",
                "player_2.name",
                "player_2.last_name",
                "player_2.id",
                "challenge.id",
                "played",
            )
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
        challenge_users: ChallengeUserModel = challenge.challenge_users.first()
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
        challenge.status = CHALLENGE_STATUS_DISPUTED
        challenge.save_to_db()
        if user.id == challenge_users.challenger_id:
            challenge_users.status_challenger = STATUS_DISPUTED
        else:
            challenge_users.status_challenged = STATUS_DISPUTED
        challenge_users.save_to_db()
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


class DisputeList(Resource):
    @classmethod
    @check_token
    @check_is_admin
    def get(cls):
        data = DisputeModel.get_all_disputes(request.args)
        items = data.items
        total = data.total
        return {
            "data": DisputeAdminSchema(
                only=(
                    "comments",
                    "id",
                    "created_at",
                    "updated_at",
                    "status",
                    "challenge_id",
                    "challenge.challenge_users.id",
                    "challenge.challenge_users.status_challenged",
                    "challenge.challenge_users.status_challenger",
                    "challenge.user_challenge_scores",
                )
            ).dump(items, many=True),
            "total": total,
        }, 200


class DisputeAdmin(Resource):
    @classmethod
    @check_token
    @check_is_admin
    def get(cls, dispute_id):
        dispute = DisputeModel.find_by_id(dispute_id)
        if dispute is None:
            return {"message": "Dispute not found"}, 404
        only = (
            "comments",
            "id",
            "created_at",
            "updated_at",
            "status",
            "challenge_id",
            "challenge.game.name",
            "challenge.console.name",
            "challenge.challenge_users.id",
            "challenge.challenge_users.status_challenged",
            "challenge.challenge_users.status_challenger",
            "challenge.user_challenge_scores",
            "user_id",
        )
        return {"data": DisputeAdminSchema(only=only).dump(dispute)}, 200

    @classmethod
    @check_token
    @check_is_admin
    def put(cls, dispute_id):
        dispute: DisputeModel = DisputeModel.find_by_id(dispute_id)
        if dispute is None:
            return {"message": "Dispute not found"}, 404
        json_data = request.get_json()
        schema = SettleDisputeSchema()
        loaded_data = schema.load(json_data)
        loaded_data["id"] = dispute_id

        # let's find the challenge
        challenge: ChallengeModel = ChallengeModel.find_by_id(dispute.challenge_id)
        if Results1v1Model.find_by_challenge_id(challenge.id) is not None:
            return {"message": "Challenge already settled"}, 400

        # let's find the challenge users
        challenge_users: ChallengeUserModel = ChallengeUserModel.find_by_wager_id(
            dispute.challenge_id
        )
        challenge_users.status_challenger = STATUS_COMPLETED
        challenge_users.status_challenged = STATUS_COMPLETED
        challenge_users.save_to_db()
        # Ponemos los estados del challenge users en complete
        cls.store_challenge_results(loaded_data, challenge_users)
        if loaded_data["score_player_1"] != loaded_data["score_player_2"]:
            cls.assign_credits_to_winner(loaded_data, challenge)
        else:
            cls.resolve_challenge_on_tie(loaded_data, challenge_users, challenge)
        # Let's record the data in results
        challenge.status = STATUS_COMPLETED
        challenge.save_to_db()
        dispute.status = DISPUTE_STATUS_SOLVED
        dispute.save_to_db()
        return {"message": "Status changed", "data": loaded_data}, 200

    @classmethod
    def store_challenge_results(cls, data, challenge_users: ChallengeUserModel):
        results = Results1v1Model()
        results.challenge_id = challenge_users.wager_id
        results.score_player_1 = data["score_player_1"]
        results.score_player_2 = data["score_player_2"]
        results.player_1_id = data["player_1_id"]
        results.player_2_id = data["player_2_id"]
        results.played = datetime.utcnow()
        if results.score_player_1 != results.score_player_2:
            results.winner_id = data["winner_id"]
        else:
            results.winner_id = None
        results.save_to_db()
        return results

    @classmethod
    def resolve_challenge_on_tie(
        cls, data, challenge_users: ChallengeUserModel, challenge: ChallengeModel
    ):
        if data["score_player_1"] == data["score_player_2"]:
            challenger_transaction = TransactionModel.find_by_user_id(
                challenge_users.challenger_id
            )
            new_transaction = TransactionModel()
            new_transaction.previous_credit_total = challenger_transaction.credit_total
            new_transaction.credit_change = challenge.buy_in
            new_transaction.credit_total = (
                challenger_transaction.credit_total + challenge.buy_in
            )
            new_transaction.challenge_id = challenge.id
            new_transaction.user_id = challenge_users.challenger_id
            new_transaction.type = TYPE_ADD
            new_transaction.save_to_db()

            challenged_transaction = TransactionModel.find_by_user_id(
                challenge_users.challenged_id
            )
            new_transaction = TransactionModel()
            new_transaction.previous_credit_total = challenged_transaction.credit_total
            new_transaction.credit_change = challenge.buy_in
            new_transaction.credit_total = (
                challenged_transaction.credit_total + challenge.buy_in
            )
            new_transaction.challenge_id = challenge.id
            new_transaction.user_id = challenge_users.challenged_id
            new_transaction.type = TYPE_ADD
            new_transaction.save_to_db()

            return True
        return False

    @classmethod
    def assign_credits_to_winner(cls, data, challenge: ChallengeModel):
        transaction = TransactionModel.find_by_user_id(data["winner_id"])
        new_transaction = TransactionModel()
        new_transaction.previous_credit_total = transaction.credit_total
        new_transaction.credit_change = challenge.reward
        new_transaction.credit_total = transaction.credit_total + challenge.reward
        new_transaction.challenge_id = challenge.id
        new_transaction.user_id = data["winner_id"]
        new_transaction.type = TYPE_ADD
        new_transaction.save_to_db()


class AcceptChallenge(Resource):
    @classmethod
    @check_token
    def post(cls, challenge_user_id):
        current_user: UserModel = UserModel.find_by_firebase_id(g.claims["user_id"])
        challenge_user: ChallengeUserModel = ChallengeUserModel.find_by_id(
            challenge_user_id
        )
        challenge = ChallengeModel.find_by_id(challenge_user.wager_id)
        transaction = TransactionModel.find_by_user_id(current_user.id)
        if challenge_user is None:
            return {"message": "Challenge user not found"}, 400
        if challenge_user.accepted:
            return {"message": "Challenge already accepted"}, 400
        if not challenge_user.open:
            return {"message": "Challenge cannot be accepted"}, 400
        if (
            current_user.id != challenge_user.challenged_id
            and challenge_user.challenged_id is not None
        ):
            return {"message": "Cannot accept challenge from a different user"}, 400
        if not has_game_console(challenge.game_id, challenge.console_id):
            return {"message": "User game console relation not matching"}, 400
        if not current_user.has_user_game(challenge.game_id, challenge.console_id):
            return {"message": "User/game not in user games"}, 400
        if transaction is None or challenge.buy_in > transaction.credit_total:
            return {"message": "Not enough credits"}, 403
        if challenge_user.challenger_id == current_user.id:
            return {"message": "Cannot accept a challenge from yourself"}, 400
        challenge_user.challenged_id = current_user.id
        challenge_user.status_challenged = STATUS_ACCEPTED
        challenge_user.save_to_db()

        challenge.status = STATUS_ACCEPTED
        challenge.save_to_db()

        new_transaction = TransactionModel()
        new_transaction.previous_credit_total = transaction.credit_total
        new_transaction.credit_change = challenge.buy_in
        new_transaction.credit_total = transaction.credit_total - challenge.buy_in
        new_transaction.challenge_id = challenge.id
        new_transaction.user_id = current_user.id
        new_transaction.type = TYPE_SUBSTRACTION
        new_transaction.save_to_db()

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
        challenge: ChallengeModel = ChallengeModel.find_by_id(challenge_user.wager_id)
        challenge.status = STATUS_REJECTED
        challenge_user.status_challenged = STATUS_DECLINED
        challenge_user.save_to_db()
        challenge.save_to_db()
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
                "game.name",
                "game.id",
                "type",
                "date",
                "buy_in",
                "reward",
                "status",
                "due_date",
                "created_at",
                "updated_at",
                "challenge_users",
                "challenge_users.status_challenged",
                "challenge_users.status_challenger",
                "challenge_users.challenged.avatar",
                "challenge_users.challenged.username",
                "challenge_users.challenged.id",
                "challenge_users.challenged.last_name",
                "challenge_users.challenged.name",
                "challenge_users.challenged.user_games.game_id",
                "challenge_users.challenged.user_games.console_id",
                "challenge_users.challenged.user_games.gamertag",
                "challenge_users.challenger.avatar",
                "challenge_users.challenger.username",
                "challenge_users.challenger.id",
                "challenge_users.challenger.last_name",
                "challenge_users.challenger.name",
                "challenge_users.challenger.user_games.game_id",
                "challenge_users.challenger.user_games.console_id",
                "challenge_users.challenger.user_games.gamertag",
                "results_1v1.winner.avatar",
                "results_1v1.winner.username",
                "results_1v1.winner.id",
                "results_1v1.winner.last_name",
                "results_1v1.winner.name",
                "results_1v1.winner.user_games.game_id",
                "results_1v1.winner.user_games.console_id",
                "results_1v1.winner.user_games.gamertag",
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
                "console.id",
                "console.name",
                "game",
                "game.id",
                "game.name",
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
                "challenge_users.challenged.username",
                "challenge_users.challenged.id",
                "challenge_users.challenged.last_name",
                "challenge_users.challenged.name",
                "challenge_users.challenger.avatar",
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
    def __init__(cls):
        cls.now: datetime = datetime.utcnow()
        cls.current_user: UserModel
        cls.challenge: ChallengeModel
        cls.challenge_users: ChallengeUserModel
        cls.user_belongs_challenge = False
        cls.user_valid_status = False
        cls.challenge_valid_status = False
        cls.tie_challenge = False

        cls.challenge_schema = ChallengeSchema(
            only=(
                "id",
                "console.id",
                "console.name",
                "game",
                "game.id",
                "game.name",
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
                "challenge_users.challenged.username",
                "challenge_users.challenged.id",
                "challenge_users.challenged.last_name",
                "challenge_users.challenged.name",
                "challenge_users.challenger.avatar",
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

    @classmethod
    @check_token
    def put(cls, challenge_id):
        try:
            cls.assign_init_values(challenge_id)
            if not cls.challenge:
                return {"message": "Challenge not found"}, 404
            if cls.challenge.status == STATUS_DISPUTED:
                return {"message": "Action not available for user"}, 403
            cls.validate_challenge_flow()
            if not cls.user_belongs_challenge:
                return {"message": "User does not belong to challenge"}, 403
            if not cls.user_valid_status:
                return {"message": "Invalid challenge user status"}, 403
            if not cls.challenge_valid_status:
                return {"message": "Invalid challenge status"}, 403
            if cls.next_status == STATUS_READY and not cls.validate_time_window():
                return {"message": "Incorrect transition for challenge"}, 403
            cls.update_challenge_user_status()
            cls.update_challenge_status()
            cls.store_challenge_user_score()
            if cls.challenge.status == STATUS_COMPLETED:
                cls.validate_challenge_scores()
                cls.store_challenge_results()
                if cls.resolve_challenge_on_tie():
                    return (
                        {
                            "message": """Challenge updated successfully.
                            There was not a winner, credits reassigned""",
                            "challenge": cls.challenge_schema.dump(cls.challenge),
                        },
                        202,
                    )
                if cls.create_dispute_on_scores_mismatch():
                    return (
                        {
                            "message": """Challenge updated successfully.
                            There was a mismatch in the scores. 
                            A dispute was open""",
                            "challenge": cls.challenge_schema.dump(cls.challenge),
                        },
                        202,
                    )
                cls.assign_credits_to_winner()
            cls.challenge.save_to_db()
            return (
                {
                    "message": "Challenge updated successfully",
                    "challenge": cls.challenge_schema.dump(cls.challenge),
                },
                200,
            )
        except Exception as e:
            print(e)
            traceback.print_exc()
            return {
                "message": "There was an error updating the challenge: " + str(e)
            }, 400

    @classmethod
    def assign_init_values(cls, challenge_id):
        cls.json_data = request.get_json()
        if cls.json_data:
            errors = user_challenge_score_schema.validate(cls.json_data, partial=True)
            if errors:
                raise Exception(errors)
        cls.challenge = ChallengeModel.find_by_id(challenge_id)
        if not cls.challenge:
            return
        cls.current_user = UserModel.find_by_firebase_id(g.claims["uid"])
        # cls.current_user = UserModel.find_by_id(cls.json_data["user_id"])
        if not cls.current_user:
            return
        cls.challenge_users = ChallengeUserModel.query.filter_by(
            wager_id=cls.challenge.id
        ).first()

    @classmethod
    def validate_challenge_flow(cls):
        cls.user_is_challenger = (
            cls.current_user.id == cls.challenge_users.challenger_id
        )
        cls.user_is_challenged = (
            cls.current_user.id == cls.challenge_users.challenged_id
        )
        cls.user_belongs_challenge = cls.user_is_challenger or cls.user_is_challenged
        user_status = cls.challenge_users.status_challenger
        rival_status = cls.challenge_users.status_challenged
        status_check_index = 1
        if cls.user_is_challenged:
            user_status = cls.challenge_users.status_challenged
            rival_status = cls.challenge_users.status_challenger
            status_check_index = 0

        current_challenge_status = cls.challenge.status
        cls.user_valid_status = (
            rival_status in _USERS_STATUS_FLOW[user_status][status_check_index]
        )
        cls.next_status = _USERS_STATUS_FLOW[user_status][2]
        cls.challenge_valid_status = (
            current_challenge_status == _USERS_STATUS_FLOW[user_status][3]
        )

    @classmethod
    def validate_time_window(cls):
        now_less_150_sec = cls.now - timedelta(seconds=150)
        now_plus_150_sec = cls.now + timedelta(seconds=150)
        return now_less_150_sec <= cls.challenge.date <= now_plus_150_sec

    @classmethod
    def update_challenge_user_status(cls):
        if cls.user_is_challenger:
            cls.challenge_users.status_challenger = cls.next_status
        elif cls.user_is_challenged:
            cls.challenge_users.status_challenged = cls.next_status
        cls.challenge_users.save_to_db()

    @classmethod
    def update_challenge_status(cls):
        challenge_users_same_status = (
            cls.challenge_users.status_challenger
            == cls.challenge_users.status_challenged
        )
        if challenge_users_same_status or cls.next_status == STATUS_DISPUTED:
            cls.challenge.status = cls.next_status

    @classmethod
    def store_challenge_user_score(cls):
        if cls.next_status == STATUS_COMPLETED:
            # {own_score: int, opponent_score: int, screenshot: str}
            user_challenge_score = UserChallengeScoresModel()
            user_challenge_score.challenge_id = cls.challenge.id
            user_challenge_score.user_id = cls.current_user.id
            user_challenge_score.own_score = cls.json_data["own_score"]
            user_challenge_score.opponent_score = cls.json_data["opponent_score"]
            user_challenge_score.screenshot = cls.json_data["screenshot"]
            user_challenge_score.save_to_db()

    @classmethod
    def validate_challenge_scores(cls):
        cls.challenger_score = UserChallengeScoresModel.find_by_challenge_id_user_id(
            cls.challenge.id, cls.challenge_users.challenger_id
        )
        cls.challenged_score = UserChallengeScoresModel.find_by_challenge_id_user_id(
            cls.challenge.id, cls.challenge_users.challenged_id
        )
        cls.same_challenger_result = (
            cls.challenger_score.own_score == cls.challenged_score.opponent_score
        )
        cls.same_challenged_result = (
            cls.challenged_score.own_score == cls.challenger_score.opponent_score
        )

    @classmethod
    def store_challenge_results(cls):
        if cls.same_challenger_result and cls.same_challenged_result:
            results = Results1v1Model()
            results.challenge_id = cls.challenge.id
            results.score_player_1 = cls.challenger_score.own_score
            results.score_player_2 = cls.challenged_score.own_score
            results.player_1_id = cls.challenge_users.challenger_id
            results.player_2_id = cls.challenge_users.challenged_id
            results.played = cls.now
            challenger_won = (
                cls.challenger_score.own_score > cls.challenged_score.own_score
            )
            challenged_won = (
                cls.challenged_score.own_score > cls.challenger_score.own_score
            )
            if challenger_won:
                results.winner_id = cls.challenge_users.challenger_id
            elif challenged_won:
                results.winner_id = cls.challenge_users.challenged_id
            else:
                cls.tie_challenge = True
            results.save_to_db()

    @classmethod
    def resolve_challenge_on_tie(cls):
        if cls.tie_challenge:
            challenger_transaction = TransactionModel.find_by_user_id(
                cls.challenge_users.challenger_id
            )
            new_transaction = TransactionModel()
            new_transaction.previous_credit_total = challenger_transaction.credit_total
            new_transaction.credit_change = cls.challenge.buy_in
            new_transaction.credit_total = (
                challenger_transaction.credit_total + cls.challenge.buy_in
            )
            new_transaction.challenge_id = cls.challenge.id
            new_transaction.user_id = cls.challenge_users.challenger_id
            new_transaction.type = TYPE_ADD
            new_transaction.save_to_db()

            challenged_transaction = TransactionModel.find_by_user_id(
                cls.challenge_users.challenged_id
            )
            new_transaction = TransactionModel()
            new_transaction.previous_credit_total = challenged_transaction.credit_total
            new_transaction.credit_change = cls.challenge.buy_in
            new_transaction.credit_total = (
                challenged_transaction.credit_total + cls.challenge.buy_in
            )
            new_transaction.challenge_id = cls.challenge.id
            new_transaction.user_id = cls.challenge_users.challenged_id
            new_transaction.type = TYPE_ADD
            new_transaction.save_to_db()

            return True
        return False

    @classmethod
    def create_dispute_on_scores_mismatch(cls):
        if not (cls.same_challenger_result or cls.same_challenged_result):
            cls.challenge_users.status_challenger = STATUS_DISPUTED
            cls.challenge_users.status_challenged = STATUS_DISPUTED
            cls.challenge.status = STATUS_DISPUTED
            cls.challenge.save_to_db()

            dispute: DisputeModel = DisputeModel()
            dispute.challenge_id = cls.challenge.id
            dispute.user_id = cls.challenge_users.challenger_id
            dispute.status = DISPUTE_STATUS_OPEN
            dispute.comments = "GENERATED AUTOMATICALLY"
            dispute.save_to_db()
            return True
        return False

    @classmethod
    def assign_credits_to_winner(cls):
        results = Results1v1Model.find_by_challenge_id(cls.challenge.id)
        transaction = TransactionModel.find_by_user_id(results.winner_id)
        new_transaction = TransactionModel()
        new_transaction.previous_credit_total = transaction.credit_total
        new_transaction.credit_change = cls.challenge.reward
        new_transaction.credit_total = transaction.credit_total + cls.challenge.reward
        new_transaction.challenge_id = cls.challenge.id
        new_transaction.user_id = results.winner_id
        new_transaction.type = TYPE_ADD
        new_transaction.save_to_db()
