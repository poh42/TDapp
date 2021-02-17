from flask_marshmallow import Schema
from marshmallow import fields


class SendMessageSchema(Schema):
    message = fields.String(required=True)
    channel_url = fields.String(required=True)
