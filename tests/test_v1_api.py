import json
import datetime

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
            "api/system-baseline/v1/baselines", headers=fixtures.AUTH_HEADER
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data)["meta"]["count"], 0)


class BadUUIDTests(unittest.TestCase):
    def setUp(self):
        test_connexion_app = app.create_app()
        test_flask_app = test_connexion_app.app
        self.client = test_flask_app.test_client()

    def test_delete_malformed_uuid(self):
        response = self.client.delete(
            "api/system-baseline/v1/baselines/MALFORMED-UUID",
            headers=fixtures.AUTH_HEADER,
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            json.loads(response.data)["message"],
            "malformed UUID requested (MALFORMED-UUID)",
        )


class InvalidFactsTests(unittest.TestCase):
    def setUp(self):
        test_connexion_app = app.create_app()
        test_flask_app = test_connexion_app.app
        self.client = test_flask_app.test_client()

    def test_large_facts(self):
        large_factset = []
        for i in range(2 ** 15):  # 32K
            large_factset.append({"name": str(i), "value": "lorem ipsum"})

        large_baseline = {
            "display_name": "large baseline",
            "baseline_facts": large_factset,
        }

        response = self.client.post(
            "api/system-baseline/v1/baselines",
            headers=fixtures.AUTH_HEADER,
            json=large_baseline,
        )

        self.assertEqual(response.status_code, 400)


class ApiTests(unittest.TestCase):
    def setUp(self):
        test_connexion_app = app.create_app()
        test_flask_app = test_connexion_app.app
        self.client = test_flask_app.test_client()
        self.client.post(
            "api/system-baseline/v1/baselines",
            headers=fixtures.AUTH_HEADER,
            json=fixtures.BASELINE_ONE_LOAD,
        )
        self.client.post(
            "api/system-baseline/v1/baselines",
            headers=fixtures.AUTH_HEADER,
            json=fixtures.BASELINE_TWO_LOAD,
        )

    def tearDown(self):
        response = self.client.get(
            "api/system-baseline/v1/baselines", headers=fixtures.AUTH_HEADER
        )
        data = json.loads(response.data)["data"]
        for baseline in data:
            response = self.client.delete(
                "api/system-baseline/v1/baselines/%s" % baseline["id"],
                headers=fixtures.AUTH_HEADER,
            )
            self.assertEqual(response.status_code, 200)

    def test_fetch_baseline_list(self):
        response = self.client.get(
            "api/system-baseline/v1/baselines", headers=fixtures.AUTH_HEADER
        )
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        self.assertEqual(result["meta"]["count"], 2)
        self.assertEqual(result["meta"]["total_available"], 2)

    def test_fetch_baseline_list_sort(self):
        response = self.client.get(
            "api/system-baseline/v1/baselines?order_by=display_name",
            headers=fixtures.AUTH_HEADER,
        )
        self.assertEqual(response.status_code, 200)
        asc_result = json.loads(response.data)
        response = self.client.get(
            "api/system-baseline/v1/baselines?order_by=display_name&order_how=DESC",
            headers=fixtures.AUTH_HEADER,
        )
        self.assertEqual(response.status_code, 200)
        desc_result = json.loads(response.data)
        # check that the ascending result is the inverse of the descending result
        self.assertEqual(desc_result["data"][::-1], asc_result["data"])

    def test_fetch_baseline_search(self):
        response = self.client.get(
            "api/system-baseline/v1/baselines?display_name=arch",
            headers=fixtures.AUTH_HEADER,
        )
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        self.assertEqual(result["meta"]["count"], 1)
        self.assertEqual(result["meta"]["total_available"], 2)
        self.assertEqual(result["data"][0]["display_name"], "arch baseline")

        response = self.client.get(
            "api/system-baseline/v1/baselines?display_name= ",
            headers=fixtures.AUTH_HEADER,
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
            "api/system-baseline/v1/baselines",
            headers=fixtures.AUTH_HEADER,
            json=fixtures.BASELINE_ONE_LOAD,
        )
        self.client.post(
            "api/system-baseline/v1/baselines",
            headers=fixtures.AUTH_HEADER,
            json=fixtures.BASELINE_TWO_LOAD,
        )

    def tearDown(self):
        response = self.client.get(
            "api/system-baseline/v1/baselines", headers=fixtures.AUTH_HEADER
        )
        data = json.loads(response.data)["data"]
        for baseline in data:
            response = self.client.delete(
                "api/system-baseline/v1/baselines/%s" % baseline["id"],
                headers=fixtures.AUTH_HEADER,
            )
            self.assertEqual(response.status_code, 200)

    def test_copy_baseline(self):
        response = self.client.get(
            "api/system-baseline/v1/baselines", headers=fixtures.AUTH_HEADER
        )
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        source_uuid = result["data"][0]["id"]

        response = self.client.post(
            "api/system-baseline/v1/baselines/%s?display_name=copy" % source_uuid,
            headers=fixtures.AUTH_HEADER,
        )
        self.assertEqual(response.status_code, 200)
        copied_baseline = json.loads(response.data)

        response = self.client.get(
            "api/system-baseline/v1/baselines/%s" % source_uuid,
            headers=fixtures.AUTH_HEADER,
        )
        original_baseline = json.loads(response.data)

        response = self.client.get(
            "api/system-baseline/v1/baselines", headers=fixtures.AUTH_HEADER
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data)["meta"]["count"], 3)

        old_date = datetime.datetime.strptime(
            original_baseline["data"][0]["created"], "%Y-%m-%dT%H:%M:%S.%fZ"
        )
        new_date = datetime.datetime.strptime(
            copied_baseline["created"], "%Y-%m-%dT%H:%M:%S.%fZ"
        )
        self.assertNotEqual(old_date, new_date)


class ApiPatchTests(unittest.TestCase):
    def setUp(self):
        test_connexion_app = app.create_app()
        test_flask_app = test_connexion_app.app
        self.client = test_flask_app.test_client()
        self.client.post(
            "api/system-baseline/v1/baselines",
            headers=fixtures.AUTH_HEADER,
            json=fixtures.BASELINE_THREE_LOAD,
        )

    def tearDown(self):
        response = self.client.get(
            "api/system-baseline/v1/baselines", headers=fixtures.AUTH_HEADER
        )
        data = json.loads(response.data)["data"]
        for baseline in data:
            response = self.client.delete(
                "api/system-baseline/v1/baselines/%s" % baseline["id"],
                headers=fixtures.AUTH_HEADER,
            )
            self.assertEqual(response.status_code, 200)

    def test_patch_baseline(self):
        # obtain the UUID for a baseline
        response = self.client.get(
            "api/system-baseline/v1/baselines", headers=fixtures.AUTH_HEADER
        )
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        patched_uuid = result["data"][0]["id"]

        # apply patch to data
        response = self.client.patch(
            "api/system-baseline/v1/baselines/%s" % patched_uuid,
            headers=fixtures.AUTH_HEADER,
            json=fixtures.BASELINE_PATCH,
        )
        self.assertEqual(response.status_code, 200)

        # confirm patch landed
        response = self.client.get(
            "api/system-baseline/v1/baselines/%s" % patched_uuid,
            headers=fixtures.AUTH_HEADER,
        )
        result = json.loads(response.data)
        for fact in result["data"][0]["baseline_facts"]:
            self.assertTrue(fact["name"] in ("nested", "nested fact 2"))

        # create a second baseline
        self.client.post(
            "api/system-baseline/v1/baselines",
            headers=fixtures.AUTH_HEADER,
            json=fixtures.BASELINE_ONE_LOAD,
        )
        # attempt to rename the first baseline to the second
        response = self.client.patch(
            "api/system-baseline/v1/baselines/%s" % patched_uuid,
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
            "api/system-baseline/v1/baselines", headers=fixtures.AUTH_HEADER
        )
        data = json.loads(response.data)["data"]
        for baseline in data:
            response = self.client.delete(
                "api/system-baseline/v1/baselines/%s" % baseline["id"],
                headers=fixtures.AUTH_HEADER,
            )
            self.assertEqual(response.status_code, 200)

    @patch("system_baseline.views.v1.fetch_systems_with_profiles")
    def test_create_from_inventory(self, mock_fetch):
        mock_fetch.return_value = [fixtures.SYSTEM_WITH_PROFILE]
        response = self.client.post(
            "api/system-baseline/v1/baselines",
            headers=fixtures.AUTH_HEADER,
            json=fixtures.CREATE_FROM_INVENTORY,
        )
        self.assertEqual(response.status_code, 200)


class ApiDuplicateTests(unittest.TestCase):
    def setUp(self):
        test_connexion_app = app.create_app()
        test_flask_app = test_connexion_app.app
        self.client = test_flask_app.test_client()

    def tearDown(self):
        response = self.client.get(
            "api/system-baseline/v1/baselines", headers=fixtures.AUTH_HEADER
        )
        data = json.loads(response.data)["data"]
        for baseline in data:
            response = self.client.delete(
                "api/system-baseline/v1/baselines/%s" % baseline["id"],
                headers=fixtures.AUTH_HEADER,
            )
            self.assertEqual(response.status_code, 200)

    def test_duplicate_baseline(self):
        response = self.client.post(
            "api/system-baseline/v1/baselines",
            headers=fixtures.AUTH_HEADER,
            json=fixtures.BASELINE_DUPLICATES_LOAD,
        )
        self.assertIn("declared more than once", response.data.decode("utf-8"))

        response = self.client.post(
            "api/system-baseline/v1/baselines",
            headers=fixtures.AUTH_HEADER,
            json=fixtures.BASELINE_DUPLICATES_TWO_LOAD,
        )
        self.assertIn("memory declared more than once", response.data.decode("utf-8"))
