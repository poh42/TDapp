from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_restful import Api
from flask_migrate import Migrate, upgrade
import os

from marshmallow import ValidationError

from ma import ma
from db import db
from resources.user import (
    UserRegister,
    UserLogin,
    # TokenRefresh,
    # UserLogout,
    # SetPassword,
)

load_dotenv(".env", verbose=True)

app = Flask(__name__)
app.secret_key = os.environ.get("APP_SECRET_KEY")
app.config.from_object("default_config")
app.config.from_envvar("APPLICATION_SETTINGS")
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024
api = Api(app)
migrate = Migrate(app, db)


@app.before_first_request
def create_tables():
    if app.config["RUN_ALEMBIC_MIGRATIONS"]:
        print("Running migrations")
        upgrade()
    else:
        print("App started without running migrations")


@app.errorhandler(ValidationError)
def handle_marshmallow_error(err):
    return jsonify(err.messages), 400


api.add_resource(UserRegister, "/register")
api.add_resource(UserLogin, "/login")
# api.add_resource(TokenRefresh, "/refresh")
# api.add_resource(UserLogout, "/logout")
# api.add_resource(SetPassword, "/user/password")

db.init_app(app)
migrate.init_app(app)

if __name__ == "__main__":
    ma.init_app(app)
    app.run(port=5000)
