import json

from . import fixtures
from . import utils


class HSPApiTests(utils.ApiTest):
    def test_status_bad_uuid(self):
        response = self.client.get(
            "/api/historical-system-profiles/v1/profiles/1",
            headers=fixtures.AUTH_HEADER,
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("too short", json.loads(response.data)["detail"])
