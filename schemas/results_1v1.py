from ma import ma
from models.results_1v1 import Results1v1Model


class Results1v1Schema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Results1v1Model
        dump_only = ("id", "created_at", "updated_at")
        load_instance = True
