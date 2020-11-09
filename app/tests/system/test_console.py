from models.console import ConsoleModel
from tests.base import BaseAPITestCase
from tests.utils import create_fixtures


class TestConsoleEndpoints(BaseAPITestCase):
    def test_confirmation_endpoint(self):
        with self.test_client() as c:
            with self.app_context():
                create_fixtures()
                rv = c.get("/consoles")
                self.assertEqual(rv.status_code, 200, "Wrong status code")
                json_data = rv.get_json()
                consoles = json_data["consoles"]

                def check_console_is_present(name):
                    for co in consoles:
                        if co["name"] == name:
                            return True
                    return False

                self.assertTrue(
                    check_console_is_present("PS1"),
                    "PS1 console is not present in the data",
                )

    def test_get_games_by_console(self):
        with self.test_client() as c:
            with self.app_context():
                fixtures = create_fixtures()
                console_without_games = ConsoleModel()
                console_without_games.name = "Console without games"
                console_without_games.save_to_db()
                console = fixtures["console"]
                with self.subTest(console_without_games=False):
                    rv = c.get(f"/console/{console.id}/games")
                    json_data = rv.get_json()
                    self.assertEqual(rv.status_code, 200, "Wrong status code")
                    self.assertEqual(json_data["message"], "Games found")
                    self.assertGreater(
                        len(json_data["games"]), 0, "It should return games"
                    )
                with self.subTest(console_without_games=True):
                    rv = c.get(f"/console/{console_without_games.id}/games")
                    json_data = rv.get_json()
                    self.assertEqual(rv.status_code, 200, "Wrong status code")
                    self.assertEqual(json_data["message"], "Games not found")
                    self.assertEqual(
                        len(json_data["games"]), 0, "It should not return games"
                    )

                with self.subTest(console_not_found=True):
                    rv = c.get(f"/console/999999999999999999999999/games") # Non existing console
                    json_data = rv.get_json()
                    self.assertEqual(rv.status_code, 400, "Wrong status code")
                    self.assertEqual(json_data["message"], "Console not found")
