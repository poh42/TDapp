from ma import ma
from models.user import UserModel
from marshmallow import fields, validate


class UserSchema(ma.SQLAlchemyAutoSchema):
    email = fields.Email()
    password = fields.String(validate=validate.Length(min=6), required=True)

    class Meta:
        model = UserModel
        load_only = ("password",)
        dump_only = ("id", "firebase_id")
        load_instance = True
