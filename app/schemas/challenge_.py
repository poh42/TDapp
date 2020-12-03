from ma import ma
from models.challenge_ import ChallengeModel
from marshmallow import fields, validate, validates_schema, ValidationError

from models.console import ConsoleModel
from models.game import GameModel
from schemas.challenge_user import ChallengeUserSchema
from schemas.console import ConsoleSchema
from schemas.game import GameSchema
from utils.validation import validate_lower_upper_fields
from schemas.results_1v1 import Results1v1Schema


def validate_game_id(data):
    if not data:
        raise ValidationError("Data not provided")
    game = GameModel.find_by_id(data)
    if game is None:
        raise ValidationError("Game id should be valid")


def validate_console_id(_id):
    if not _id:
        raise ValidationError("Data not provided")
    game = ConsoleModel.console_id_exists(_id)
    if game is None:
        raise ValidationError("Console id should be valid")


class ChallengeSchema(ma.SQLAlchemyAutoSchema):
    results_1v1 = fields.Nested(Results1v1Schema)
    game = fields.Nested(GameSchema)
    game_id = fields.Integer(required=True, validate=validate_game_id)
    challenge_users = fields.Nested(ChallengeUserSchema, many=True)
    console_id = fields.Integer(required=True, validate=validate_console_id)
    console = fields.Nested(ConsoleSchema)

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
        dump_only = ("id", "created_at", "updated_at", "results", "game", "console")
        load_instance = True
