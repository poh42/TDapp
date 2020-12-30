from flask import request
from flask_restful import Resource

from decorators import check_token, check_is_admin
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

    @classmethod
    @check_token
    @check_is_admin
    def post(cls):
        console: ConsoleModel = console_schema.load(request.get_json())
        if ConsoleModel.console_name_exists(console.name):
            return {"message": "Console already exists"}, 400
        console.save_to_db()
        return {"console": console_schema.dump(console)}, 201


class Console(Resource):
    @classmethod
    @check_token
    @check_is_admin
    def put(cls):
        pass
