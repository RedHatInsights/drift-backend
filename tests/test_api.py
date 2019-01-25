from drift import app
import json

import unittest


class ApiTests(unittest.TestCase):

    def setUp(self):
        test_app = app.create_app()
        self.client = test_app.test_client()

    def test_status_api(self):
        response = self.client.get("r/insights/platform/drift/v0/status")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data), {'status': 'running'})

    def test_compare_api(self):
        response = self.client.get("r/insights/platform/drift/v0/compare")
        self.assertEqual(response.status_code, 200)
