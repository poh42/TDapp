from datetime import datetime, timedelta

from sqlalchemy import and_, select, func
from sqlalchemy.orm import aliased

from db import db

from models.challenge_ import ChallengeModel
from models.challenge_user import ChallengeUserModel
from models.results_1v1 import Results1v1Model
from models.transaction import TransactionModel, TYPE_ADD
from models.user_challenge_scores import UserChallengeScoresModel


def get_challenges_that_need_finish():
    now = datetime.utcnow()
    begin = now - timedelta(days=1, minutes=30)
    end = now - timedelta(days=1)

    count_scores_query = (
        db.session.query(
            UserChallengeScoresModel.challenge_id,
            func.count("*").label("user_scores_count"),
        )
        .group_by(UserChallengeScoresModel.challenge_id)
        .subquery()
    )

    results_1v1 = aliased(ChallengeModel.results_1v1)

    # Main query
    challenges = (
        ChallengeModel.query.join(
            count_scores_query, count_scores_query.c.challenge_id == ChallengeModel.id
        )
        .join(results_1v1, isouter=True)
        .filter(
            and_(
                ChallengeModel.due_date >= begin,
                ChallengeModel.due_date <= end,
                count_scores_query.c.user_scores_count == 1,
                results_1v1.challenge_id == None,
            )
        )
    )
    print(challenges)
    return challenges.all()


def get_winner_challenge(challenge_score, challenge_user):
    print("get user challenge", challenge_score, challenge_user)
    if challenge_score.did_win_challenge:
        return challenge_score.user_id
    else:
        if challenge_score.user_id == challenge_user.challenged_id:
            return challenge_user.challenger_id
        else:
            return challenge_user.challenged_id


def set_finished_challenges_results(challenge):
    challenge_score: UserChallengeScoresModel = UserChallengeScoresModel.query.filter(
        UserChallengeScoresModel.challenge_id == challenge.id
    ).first()
    challenge_user = challenge.challenge_user.first()
    store_challenge_results(challenge_score, challenge_user)
    if challenge_score.own_score != challenge_score.opponent_score:
        print("Assigning credits to winner", challenge)
        assign_credits_to_winner(challenge_score, challenge)
    else:
        print("Resolving on tie", challenge)
        resolve_challenge_on_tie(challenge_score, challenge_user, challenge)


def store_challenge_results(
    data: UserChallengeScoresModel, challenge_users: ChallengeUserModel
):
    if data.user_id == challenge_users.challenged_id:
        player_2_id = challenge_users.challenger_id
    else:
        player_2_id = challenge_users.challenged_id
    results = Results1v1Model()
    results.challenge_id = challenge_users.wager_id
    results.score_player_1 = data.own_score
    results.score_player_2 = data.opponent_score
    results.player_1_id = data.user_id
    results.player_2_id = player_2_id
    results.played = datetime.utcnow()
    if results.score_player_1 > results.score_player_2:
        results.winner_id = data.user_id
    elif results.score_player_1 < results.score_player_2:
        results.winner_id = player_2_id
    else:
        results.winner_id = None
    results.save_to_db()
    return results


def resolve_challenge_on_tie(
    data: UserChallengeScoresModel,
    challenge_users: ChallengeUserModel,
    challenge: ChallengeModel,
):
    if data.own_score == data.opponent_score:
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


def assign_credits_to_winner(challenge: ChallengeModel):
    winner_id = get_winner_challenge(challenge)
    transaction = TransactionModel.find_by_user_id(winner_id)
    new_transaction = TransactionModel()
    new_transaction.previous_credit_total = transaction.credit_total
    new_transaction.credit_change = challenge.reward
    new_transaction.credit_total = transaction.credit_total + challenge.reward
    new_transaction.challenge_id = challenge.id
    new_transaction.user_id = winner_id
    new_transaction.type = TYPE_ADD
    new_transaction.save_to_db()


def main():
    challenges = get_challenges_that_need_finish()
    print("Challenges found", challenges)
    for c in challenges:
        print("Setting finished challenge", c)
        set_finished_challenges_results(c)
        print("Fixed challenge")
