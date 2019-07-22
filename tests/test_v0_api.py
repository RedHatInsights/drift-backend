import json

from system_baseline import app

import unittest

from . import fixtures


class EmptyApiTests(unittest.TestCase):
    def setUp(self):
        test_connexion_app = app.create_app()
        test_flask_app = test_connexion_app.app
        self.client = test_flask_app.test_client()

    def test_fetch_empty_baseline_list(self):
        response = self.client.get(
            "api/system-baseline/v0/baselines", headers=fixtures.AUTH_HEADER
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data)["meta"]["count"], 0)


class ApiTests(unittest.TestCase):
    def setUp(self):
        test_connexion_app = app.create_app()
        test_flask_app = test_connexion_app.app
        self.client = test_flask_app.test_client()
        self.client.post(
            "api/system-baseline/v0/baselines",
            headers=fixtures.AUTH_HEADER,
            json=fixtures.BASELINE_LOAD,
        )

    def tearDown(self):
        response = self.client.get(
            "api/system-baseline/v0/baselines", headers=fixtures.AUTH_HEADER
        )
        data = json.loads(response.data)["data"]
        for baseline in data:
            self.client.delete(
                "api/system-baseline/v0/baselines/%s" % baseline["id"],
                headers=fixtures.AUTH_HEADER,
            )

    def test_fetch_baseline_list(self):
        response = self.client.get(
            "api/system-baseline/v0/baselines", headers=fixtures.AUTH_HEADER
        )
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        self.assertEqual(result["meta"]["count"], 2)
