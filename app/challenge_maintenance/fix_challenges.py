from datetime import datetime, timedelta

from sqlalchemy import and_, select, func
from db import db

from models.challenge_ import ChallengeModel
from models.user_challenge_scores import UserChallengeScoresModel


def get_challenges_that_need_finish():
    now = datetime.utcnow()
    begin = now - timedelta(days=1, minutes=30)
    end = now - timedelta(days=1)

    count_query = db.session.query(
        UserChallengeScoresModel.challenge_id, func.count("*").label("user_scores_count")
    ).group_by(UserChallengeScoresModel.challenge_id).subquery()

    # Main query
    challenges = ChallengeModel.query.join(count_query, count_query.c.challenge_id == ChallengeModel.id).filter(
        and_(
            ChallengeModel.due_date >= begin,
            ChallengeModel.due_date <= end,
            count_query.c.user_scores_count == 1
        )
    )
    return challenges.all()


def set_finished_challenges_results():
    pass

