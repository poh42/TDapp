from marshmallow import Schema, fields


class ResendConfirmationSchema(Schema):
    email = fields.String(required=True)