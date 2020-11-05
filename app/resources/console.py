from flask_restful import Resource
from models.console import ConsoleModel
from schemas.console import ConsoleSchema

console_schema = ConsoleSchema()


class ConsoleList(Resource):
    @classmethod
    def get(cls):
        consoles = ConsoleModel.get_all_consoles()
        return {
            "message": "Consoles found",
            "consoles": console_schema.dump(consoles, many=True),
        }
