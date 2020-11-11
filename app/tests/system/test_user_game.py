import json

from models.user_game import UserGameModel
from tests.base import BaseAPITestCase
from tests.utils import create_fixtures


class TestUserGameEndpoints(BaseAPITestCase):
    def test_put_user_game(self):
        with self.app_context():
            fixtures = create_fixtures()
            user = fixtures["user_login"]
            console = fixtures["console"]
            game = fixtures["game"]
            gamertag = "test"
            data = dict(console_id=console.id, game_id=game.id, gamertag=gamertag)
            with self.test_client() as c:
                rv = c.put(
                    f"/user/{user.id}/addToLibrary",
                    data=json.dumps(data),
                    content_type="application/json",
                )
                self.assertEqual(rv.status_code, 200, "Wrong status code")
                self.assertIsNotNone(
                    UserGameModel.query.filter_by(
                        console_id=console.id,
                        user_id=user.id,
                        game_id=game.id,
                        gamertag=gamertag,
                    ).first(),
                    "User game model was not saved",
                )
