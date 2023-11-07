import json
import unittest

from drift import app


class ManagementApiTests(unittest.TestCase):
    def setUp(self):
        test_connexion_app = app.create_app()
        self.client = test_connexion_app.test_client()

    def test_status(self):
        response = self.client.get("mgmt/v0/status")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {"status": "running"})

    def test_metrics(self):
        response = self.client.get("mgmt/v0/metrics")
        # the response will contain stats for calls made by other unit
        # tests. Just check for a 200.
        self.assertEqual(response.status_code, 200)
