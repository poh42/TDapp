from dotenv import load_dotenv
from flask import Flask, jsonify, make_response, send_from_directory, redirect
from flask_restful import Api
from flask_migrate import Migrate, upgrade
import os
import sys
import simplejson
import logging

from marshmallow import ValidationError

from ma import ma
from db import db
from resources.user import (
    UserRegister,
    UserLogin,
    SetAdminStatus,
    User,
)

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
log = logging.getLogger(__name__)

if "unittest" in sys.modules.keys():
    # tests are running
    log.info("Loading .env.test environment variables")
    current_path = os.path.dirname(__file__)
    load_dotenv(os.path.join(current_path, ".env.test"), verbose=True)
else:
    # Tests are not running
    log.info("Loading .env environment variables")
    load_dotenv(".env", verbose=True)

app = Flask(__name__)
app.secret_key = os.environ.get("APP_SECRET_KEY")
app.config.from_object("default_config")
app.config.from_envvar("APPLICATION_SETTINGS")
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024
api = Api(app)
migrate = Migrate(app, db)


@api.representation("application/json")
def output_json(data, code, headers=None):
    resp = make_response(simplejson.dumps(data), code)
    resp.headers.extend(headers or {})
    return resp


@app.before_first_request
def create_tables():
    if app.config["RUN_ALEMBIC_MIGRATIONS"]:
        log.info("Running migrations")
        upgrade()
    else:
        log.info("App started without running migrations")


@app.errorhandler(ValidationError)
def handle_marshmallow_error(err):
    return jsonify(err.messages), 400


@app.route("/docs")
def send_index_docs():
    return redirect("/docs/index.html")


@app.route("/docs/<path:path>")
def send_docs(path=None):
    return send_from_directory("docs", path)


api.add_resource(UserRegister, "/register")
api.add_resource(UserLogin, "/login")
api.add_resource(SetAdminStatus, "/set_admin/<int:user_id>")
api.add_resource(User, "/user/<int:user_id>")

db.init_app(app)
migrate.init_app(app)

if __name__ == "__main__":
    ma.init_app(app)
    app.run(port=5000)
