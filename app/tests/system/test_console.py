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

                self.assertTrue(check_console_is_present("PS1"), "PS1 console is not present in the data")
