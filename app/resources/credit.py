from flask import request, g
from flask_restful import Resource
from sqlalchemy.sql import text
from db import db
from decorators import check_token, check_is_admin
from models.user import UserModel

sql = """
insert into transactions (previous_credit_total, credit_change, credit_total, user_id, type) with summary as (
select
    t.user_id,
    t.credit_total,
    row_number() over (partition by t.user_id
order by
    t.created_at desc) as rn
from
    transactions t )
select
    summary.credit_total as previous_credit_total,
    :credit_change as credit_change, 
    summary.credit_total + :credit_change as credit_total,
    summary.user_id as user_id,
    'ADD' as type
from
    summary
where
    summary.rn = 1
    and summary.credit_total < :threshold
"""


class AddCredits(Resource):
    @classmethod
    @check_token
    @check_is_admin
    def post(cls):
        json_data = request.get_json()
        if (
            json_data is None
            or "threshold" not in json_data
            or "credit_change" not in json_data
        ):
            return {
                "message": "'threshold' and 'credit_change' must be in json data"
            }, 400
        stmt = text(sql)
        db.engine.execute(
            stmt,
            threshold=json_data["threshold"],
            credit_change=json_data["credit_change"],
        )
        return {"message": "Credits added"}, 201


class Credit(Resource):
    @classmethod
    @check_token
    def get(cls):
        user: UserModel = UserModel.find_by_firebase_id(g.claims["uid"])
        if not user:
            return {"message": "User not found"}, 404
        return {"credit_total": user.get_credits()}, 200
