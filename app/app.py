from flask import Flask, jsonify, make_response, send_from_directory, redirect
from flask_restful import Api
from flask_migrate import Migrate, upgrade
from flask_cors import CORS
import os
import sys
import simplejson
import logging

from marshmallow import ValidationError

from ma import ma
from db import db
from resources.confirmation import Confirmation, ConfirmationByUser
from resources.challenge_ import (
    Challenge,
    ChallengeList,
    ResultsByUser,
    ChallengePerson,
    ChallengeResults,
    ReportChallenge,
    ChallengePost,
    GetDisputes,
    AcceptChallenge,
    DeclineChallenge,
    ChallengesByUser,
)
from resources.console import ConsoleList
from resources.game import GamesByConsole, Games
from resources.user import (
    UserRegister,
    UserLogin,
    SetAdminStatus,
    User,
    UserList,
    UserGamesLibrary,
    AddFriend,
    RemoveFriend,
    AddUserInvite,
    DeclineInvite, AcceptInvite,
)
from flask_uploads import configure_uploads, IMAGES
from utils.image_helper import IMAGE_SET
from resources.image import ImageUpload

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
log = logging.getLogger(__name__)

if "unittest" in sys.modules.keys():
    # tests are running
    log.info("Loading .env.test environment variables")
    current_path = os.path.dirname(__file__)
else:
    # Tests are not running
    log.info("Loading .env environment variables")

app = Flask(__name__)
CORS(app)
app.secret_key = os.environ.get("APP_SECRET_KEY")
app.config.from_object("default_config")
app.config.from_envvar("APPLICATION_SETTINGS")
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024
configure_uploads(app, IMAGE_SET)
api = Api(app)
migrate = Migrate(app, db)


@api.representation("application/json")
def output_json(data, code, headers=None):
    resp = make_response(simplejson.dumps(data, default=str), code)
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


@app.cli.command("create_fixtures")
def create_fixtures_command():
    from tests.utils import create_fixtures

    create_fixtures()


api.add_resource(UserRegister, "/user/register")
api.add_resource(UserLogin, "/user/login")
api.add_resource(SetAdminStatus, "/user/set_admin/<int:user_id>")
api.add_resource(User, "/user/<int:user_id>")
api.add_resource(UserList, "/users")
api.add_resource(Confirmation, "/user/confirm/<string:confirmation_id>")
api.add_resource(ConfirmationByUser, "/confirmation/user/<int:user_id>")
api.add_resource(Challenge, "/challenge/<int:challenge_id>")
api.add_resource(ChallengePost, "/challenge")
api.add_resource(ChallengeList, "/challenges")
api.add_resource(ImageUpload, "/upload/image")
api.add_resource(GamesByConsole, "/console/<int:console_id>/games")
api.add_resource(ResultsByUser, "/challenges/<int:user_id>/getResultsUser")
api.add_resource(ChallengePerson, "/challenge/<int:challenged_id>/create")
api.add_resource(ChallengeResults, "/challenge/<int:challenge_id>/getResultsChallenge")
api.add_resource(ReportChallenge, "/challenge/<int:challenge_id>/report")
api.add_resource(GetDisputes, "/challenge/<int:challenge_id>/report/dispute")
api.add_resource(Games, "/games")
api.add_resource(AcceptChallenge, "/challenge/<int:challenge_user_id>/accept")
api.add_resource(DeclineChallenge, "/challenge/<int:challenge_user_id>/decline")
api.add_resource(ConsoleList, "/consoles")
api.add_resource(ChallengesByUser, "/challenge/<int:user_id>/user")
api.add_resource(UserGamesLibrary, "/user/<int:user_id>/addToLibrary")
api.add_resource(AddFriend, "/user/<int:user_id>/addFriend")
api.add_resource(RemoveFriend, "/user/<int:user_id>/deleteFriend")
api.add_resource(AddUserInvite, "/user/invites/<int:user_id>/create")
api.add_resource(DeclineInvite, "/user/invites/<int:invite_id>/reject")
api.add_resource(AcceptInvite, "/user/invites/<int:invite_id>/accept")

db.init_app(app)
migrate.init_app(app)

if __name__ == "__main__":
    ma.init_app(app)
    app.run(port=5000)
