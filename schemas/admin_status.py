from ma import ma
from marshmallow import fields


class AdminStatusSchema(ma.Schema):
    is_admin = fields.Boolean(required=True)
