from flask import request
from flask_restful import Resource
from marshmallow import ValidationError

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
    def put(cls, console_id):
        console: ConsoleModel = ConsoleModel.find_by_id(console_id)
        if not console:
            return {"message": "Console not found"}, 400
        json_data = request.get_json()
        errors = console_schema.validate(json_data, partial=True)
        if errors:
            raise ValidationError(errors)
        if json_data.get("name") and console.name != json_data["name"]:
            if ConsoleModel.console_name_exists(json_data["name"]):
                raise ValidationError({"name": "Console name already in use"})
            console.name = json_data["name"]
        if json_data.get("is_active") is not None:
            console.is_active = json_data["is_active"]
        console.save_to_db()
        console_schema_dump = ConsoleSchema(only=("id", "name", "is_active"))
        return {"message": "Edit successful", "console": console_schema_dump.dump(console)}
