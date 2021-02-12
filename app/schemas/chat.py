from flask_marshmallow import Schema, fields


class SendMessageSchema(Schema):
    message = fields.String(required=True)
    channel_url = fields.String(required=True)
