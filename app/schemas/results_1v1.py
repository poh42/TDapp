from ma import ma
from models.results_1v1 import Results1v1Model
from marshmallow import fields
from schemas.user import UserSchema


class Results1v1Schema(ma.SQLAlchemyAutoSchema):
    player_1 = fields.Nested(UserSchema)
    player_2 = fields.Nested(UserSchema)
    winner = fields.Nested(UserSchema)
    challenge = fields.Nested(
        "ChallengeSchema",
        only=("console.name", "console.id", "game.name", "game.id", "id", "reward"),
    )

    class Meta:
        model = Results1v1Model
        dump_only = (
            "id",
            "created_at",
            "updated_at",
            "player_1_id",
            "player_2_id",
            "player_1",
            "player_2",
        )
        load_instance = True
