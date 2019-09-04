import json

from system_baseline import app

import unittest
from mock import patch

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
            json=fixtures.BASELINE_ONE_LOAD,
        )
        self.client.post(
            "api/system-baseline/v0/baselines",
            headers=fixtures.AUTH_HEADER,
            json=fixtures.BASELINE_TWO_LOAD,
        )

    def tearDown(self):
        response = self.client.get(
            "api/system-baseline/v0/baselines", headers=fixtures.AUTH_HEADER
        )
        data = json.loads(response.data)["data"]
        for baseline in data:
            response = self.client.delete(
                "api/system-baseline/v0/baselines/%s" % baseline["id"],
                headers=fixtures.AUTH_HEADER,
            )
            self.assertEqual(response.status_code, 200)

    def test_fetch_baseline_list(self):
        response = self.client.get(
            "api/system-baseline/v0/baselines", headers=fixtures.AUTH_HEADER
        )
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        self.assertEqual(result["meta"]["count"], 2)


class CopyBaselineTests(unittest.TestCase):
    def setUp(self):
        test_connexion_app = app.create_app()
        test_flask_app = test_connexion_app.app
        self.client = test_flask_app.test_client()
        self.client.post(
            "api/system-baseline/v0/baselines",
            headers=fixtures.AUTH_HEADER,
            json=fixtures.BASELINE_ONE_LOAD,
        )
        self.client.post(
            "api/system-baseline/v0/baselines",
            headers=fixtures.AUTH_HEADER,
            json=fixtures.BASELINE_TWO_LOAD,
        )

    def tearDown(self):
        response = self.client.get(
            "api/system-baseline/v0/baselines", headers=fixtures.AUTH_HEADER
        )
        data = json.loads(response.data)["data"]
        for baseline in data:
            response = self.client.delete(
                "api/system-baseline/v0/baselines/%s" % baseline["id"],
                headers=fixtures.AUTH_HEADER,
            )
            self.assertEqual(response.status_code, 200)

    def test_copy_baseline(self):
        response = self.client.get(
            "api/system-baseline/v0/baselines", headers=fixtures.AUTH_HEADER
        )
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        source_uuid = result["data"][0]["id"]

        response = self.client.post(
            "api/system-baseline/v0/baselines/%s?display_name=copy" % source_uuid,
            headers=fixtures.AUTH_HEADER,
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            "api/system-baseline/v0/baselines", headers=fixtures.AUTH_HEADER
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data)["meta"]["count"], 3)


class ApiPatchTests(unittest.TestCase):
    def setUp(self):
        test_connexion_app = app.create_app()
        test_flask_app = test_connexion_app.app
        self.client = test_flask_app.test_client()
        self.client.post(
            "api/system-baseline/v0/baselines",
            headers=fixtures.AUTH_HEADER,
            json=fixtures.BASELINE_THREE_LOAD,
        )

    def tearDown(self):
        response = self.client.get(
            "api/system-baseline/v0/baselines", headers=fixtures.AUTH_HEADER
        )
        data = json.loads(response.data)["data"]
        for baseline in data:
            response = self.client.delete(
                "api/system-baseline/v0/baselines/%s" % baseline["id"],
                headers=fixtures.AUTH_HEADER,
            )
            self.assertEqual(response.status_code, 200)

    def test_patch_baseline(self):
        # obtain the UUID for a baseline
        response = self.client.get(
            "api/system-baseline/v0/baselines", headers=fixtures.AUTH_HEADER
        )
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        patched_uuid = result["data"][0]["id"]

        # apply patch to data
        response = self.client.patch(
            "api/system-baseline/v0/baselines/%s" % patched_uuid,
            headers=fixtures.AUTH_HEADER,
            json=fixtures.BASELINE_PARTIAL_ONE,
        )
        self.assertEqual(response.status_code, 200)

        # confirm patch landed
        response = self.client.get(
            "api/system-baseline/v0/baselines/%s" % patched_uuid,
            headers=fixtures.AUTH_HEADER,
        )
        result = json.loads(response.data)
        for fact in result["data"][0]["baseline_facts"]:
            self.assertTrue(fact["name"] in ("nested", "hello"))

        # apply nested patch to data
        response = self.client.patch(
            "api/system-baseline/v0/baselines/%s" % patched_uuid,
            headers=fixtures.AUTH_HEADER,
            json=fixtures.BASELINE_PARTIAL_TWO,
        )
        self.assertEqual(response.status_code, 200)

        # confirm patch landed
        response = self.client.get(
            "api/system-baseline/v0/baselines/%s" % patched_uuid,
            headers=fixtures.AUTH_HEADER,
        )
        result = json.loads(response.data)
        self.assertEqual("ABCDE", result["data"][0]["display_name"])
        for fact in result["data"][0]["baseline_facts"]:
            self.assertTrue(fact["name"] in ("nested", "hello"))
            if fact["name"] == "hello":
                self.assertNotIn("value", fact)  # confirm we got rid of non-nested data
                self.assertEqual(len(fact["values"]), 2)

        # create a second baseline
        self.client.post(
            "api/system-baseline/v0/baselines",
            headers=fixtures.AUTH_HEADER,
            json=fixtures.BASELINE_ONE_LOAD,
        )
        # attempt to rename the first baseline to the second
        response = self.client.patch(
            "api/system-baseline/v0/baselines/%s" % patched_uuid,
            headers=fixtures.AUTH_HEADER,
            json=fixtures.BASELINE_PARTIAL_CONFLICT,
        )
        self.assertEqual(response.status_code, 400)


class CreateFromInventoryTests(unittest.TestCase):
    def setUp(self):
        test_connexion_app = app.create_app()
        test_flask_app = test_connexion_app.app
        self.client = test_flask_app.test_client()

    def tearDown(self):
        response = self.client.get(
            "api/system-baseline/v0/baselines", headers=fixtures.AUTH_HEADER
        )
        data = json.loads(response.data)["data"]
        for baseline in data:
            response = self.client.delete(
                "api/system-baseline/v0/baselines/%s" % baseline["id"],
                headers=fixtures.AUTH_HEADER,
            )
            self.assertEqual(response.status_code, 200)

    @patch("system_baseline.views.v0.fetch_systems_with_profiles")
    def test_create_from_inventory(self, mock_fetch):
        mock_fetch.return_value = [fixtures.SYSTEM_WITH_PROFILE]
        response = self.client.post(
            "api/system-baseline/v0/baselines",
            headers=fixtures.AUTH_HEADER,
            json=fixtures.CREATE_FROM_INVENTORY,
        )
        self.assertEqual(response.status_code, 200)
