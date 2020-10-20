from ma import ma
from models.challenge_ import ChallengeModel
from marshmallow import fields, validate, validates_schema
from utils.validation import validate_lower_upper_fields


class ChallengeSchema(ma.SQLAlchemyAutoSchema):
    @validates_schema
    def validate_related_fields(self, data, **kwargs):
        validate_lower_upper_fields(
            data,
            "buy_in",
            "reward",
            "buy_in and reward should be specified together",
            "buy_in should be smaller than reward",
        )

    class Meta:
        model = ChallengeModel
        dump_only = ("id", "created_at", "updated_at")
        load_instance = True
