from ma import ma
from models.console import ConsoleModel


class ConsoleSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ConsoleModel
        dump_only = ("id", "created_at", "updated_at")
        load_instance = True
