from datetime import datetime, timedelta

from sqlalchemy import and_, select, func
from db import db

from models.challenge_ import ChallengeModel
from models.user_challenge_scores import UserChallengeScoresModel


def get_challenges_that_need_finish():
    now = datetime.utcnow()
    begin = now - timedelta(days=1, minutes=30)
    end = now - timedelta(days=1)

    count_query = (
        db.session.query(
            UserChallengeScoresModel.challenge_id,
            func.count("*").label("user_scores_count"),
        )
        .group_by(UserChallengeScoresModel.challenge_id)
        .subquery()
    )

    # Main query
    challenges = ChallengeModel.query.join(
        count_query, count_query.c.challenge_id == ChallengeModel.id
    ).filter(
        and_(
            ChallengeModel.due_date >= begin,
            ChallengeModel.due_date <= end,
            count_query.c.user_scores_count == 1,
        )
    )
    return challenges.all()


def get_user_challenge(challenge):
    challenge_score = UserChallengeScoresModel.query.filter(
        UserChallengeScoresModel.challenge_id == challenge.id
    ).first()
    challenge_user = challenge.challenge_user.first()
    print("get user challenge", challenge_score, challenge_user)
    if challenge_score.user_id == challenge_user.challenger_id:
        return challenge_user.challenger_id
    else:
        return challenge_user.challenged_id


def set_finished_challenges_results():
    pass
