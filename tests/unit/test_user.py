import unittest
from resources.user import SetAdminStatus


class TestUserEndpointDecorators(unittest.TestCase):
    def test_set_admin_status(self):
        self.assertTrue(
            SetAdminStatus.post.is_checked_by_token,
            "Endpoint is not protected by token",
        )
        self.assertTrue(
            SetAdminStatus.post.is_checked_by_admin_claim,
            "Endpoint can be accessed by other users that are not administrators",
        )
