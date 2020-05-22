import json
import datetime

from system_baseline import app
from kerlescan.exceptions import ItemNotReturned

import unittest
from mock import patch

from . import fixtures


class ApiTest(unittest.TestCase):
    def setUp(self):
        self.rbac_patcher = patch(
            "system_baseline.views.v1.view_helpers.ensure_has_role"
        )
        patched_rbac = self.rbac_patcher.start()
        patched_rbac.return_value = None  # validate all RBAC requests
        self.addCleanup(self.stopPatches)
        test_connexion_app = app.create_app()
        test_flask_app = test_connexion_app.app
        self.client = test_flask_app.test_client()

    def stopPatches(self):
        self.rbac_patcher.stop()


class EmptyApiTests(ApiTest):
    def test_fetch_empty_baseline_list(self):
        response = self.client.get(
            "api/system-baseline/v1/baselines", headers=fixtures.AUTH_HEADER
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data)["meta"]["count"], 0)


class BadUUIDTests(ApiTest):
    def test_delete_malformed_uuid(self):
        response = self.client.delete(
            "api/system-baseline/v1/baselines/MALFORMED-UUID",
            headers=fixtures.AUTH_HEADER,
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            json.loads(response.data)["message"],
            "malformed UUIDs requested (MALFORMED-UUID)",
        )


class InvalidFactsTests(ApiTest):
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

    def test_long_name_value(self):
        response = self.client.post(
            "api/system-baseline/v1/baselines",
            headers=fixtures.AUTH_HEADER,
            json=fixtures.BASELINE_LONG_NAME_LOAD,
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            "is over 500 characters", response.data.decode("utf-8"),
        )

        response = self.client.post(
            "api/system-baseline/v1/baselines",
            headers=fixtures.AUTH_HEADER,
            json=fixtures.BASELINE_LONG_VALUE_LOAD,
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            "is over 1000 characters", response.data.decode("utf-8"),
        )


class ApiSortTests(ApiTest):
    def setUp(self):
        super(ApiSortTests, self).setUp()
        self.client.post(
            "api/system-baseline/v1/baselines",
            headers=fixtures.AUTH_HEADER,
            json=fixtures.BASELINE_UNSORTED_LOAD,
        )

    def tearDown(self):
        super(ApiSortTests, self).tearDown()
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

    def test_fetch_sorted_baseline_facts(self):
        response = self.client.get(
            "api/system-baseline/v1/baselines", headers=fixtures.AUTH_HEADER
        )
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        self.assertEqual(result["meta"]["count"], 1)
        response = self.client.get(
            "api/system-baseline/v1/baselines/%s" % result["data"][0]["id"],
            headers=fixtures.AUTH_HEADER,
        )
        result = json.loads(response.data)
        # confirm that we get sorted names back, including nested names
        self.assertEqual(
            result["data"][0]["baseline_facts"],
            [
                {"name": "A-name", "value": "64GB"},
                {
                    "name": "B-name",
                    "values": [
                        {"name": "a-nested_cpu_sockets", "value": "32"},
                        {"name": "b-nested_cpu_sockets", "value": "32"},
                        {"name": "Z-nested_cpu_sockets", "value": "32"},
                    ],
                },
                {"name": "C-name", "value": "128GB"},
                {"name": "D-name", "value": "16"},
            ],
        )


class ApiGeneralTests(ApiTest):
    def setUp(self):
        super(ApiGeneralTests, self).setUp()
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
        super(ApiGeneralTests, self).tearDown()
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

    def test_value_values(self):
        response = self.client.post(
            "api/system-baseline/v1/baselines",
            headers=fixtures.AUTH_HEADER,
            json=fixtures.BASELINE_VALUE_VALUES_LOAD,
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            "fact arch cannot have value and values defined",
            response.data.decode("utf-8"),
        )

    def test_fetch_baseline_list(self):
        response = self.client.get(
            "api/system-baseline/v1/baselines", headers=fixtures.AUTH_HEADER
        )
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        self.assertEqual(result["meta"]["count"], 2)
        self.assertEqual(result["meta"]["total_available"], 2)

    def test_fetch_baseline_list_sort_display_name(self):
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

    def test_create_deletion_request(self):
        response = self.client.get(
            "api/system-baseline/v1/baselines", headers=fixtures.AUTH_HEADER
        )
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        ids_to_delete = [b["id"] for b in result["data"]]
        response = self.client.post(
            "api/system-baseline/v1/baselines/deletion_request",
            headers=fixtures.AUTH_HEADER,
            json={"baseline_ids": ids_to_delete},
        )
        self.assertEqual(response.status_code, 200)

    def test_fetch_baseline_list_sort_updated(self):
        # modify one baseline
        response = self.client.get(
            "api/system-baseline/v1/baselines", headers=fixtures.AUTH_HEADER
        )
        self.assertEqual(response.status_code, 200)
        uuid_to_modify = json.loads(response.data)["data"][0]["id"]
        response = self.client.patch(
            "api/system-baseline/v1/baselines/%s" % uuid_to_modify,
            headers=fixtures.AUTH_HEADER,
            json=fixtures.BASELINE_TOUCH,
        )
        self.assertEqual(response.status_code, 200)
        # ensure modified baseline is in the right place of the sort
        response = self.client.get(
            "api/system-baseline/v1/baselines?order_by=updated",
            headers=fixtures.AUTH_HEADER,
        )
        self.assertEqual(response.status_code, 200)
        asc_result = json.loads(response.data)
        self.assertEqual(asc_result["data"][1]["id"], uuid_to_modify)

        response = self.client.get(
            "api/system-baseline/v1/baselines?order_by=updated&order_how=DESC",
            headers=fixtures.AUTH_HEADER,
        )
        self.assertEqual(response.status_code, 200)
        desc_result = json.loads(response.data)
        # check that the ascending result is the inverse of the descending result
        self.assertEqual(desc_result["data"][::-1], asc_result["data"])

    def test_fetch_duplicate_uuid(self):
        response = self.client.get(
            "api/system-baseline/v1/baselines?display_name=arch",
            headers=fixtures.AUTH_HEADER,
        )
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        uuid = result["data"][0]["id"]
        response = self.client.get(
            "api/system-baseline/v1/baselines/%s,%s" % (uuid, uuid),
            headers=fixtures.AUTH_HEADER,
        )
        self.assertEqual(response.status_code, 400)

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

        response = self.client.get(
            "api/system-baseline/v1/baselines?display_name=a_ch",
            headers=fixtures.AUTH_HEADER,
        )
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        self.assertEqual(result["meta"]["count"], 0)

        response = self.client.post(
            "api/system-baseline/v1/baselines",
            headers=fixtures.AUTH_HEADER,
            json=fixtures.BASELINE_UNDERSCORE_LOAD,
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            "api/system-baseline/v1/baselines?display_name=has_an_underscore",
            headers=fixtures.AUTH_HEADER,
        )
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        self.assertEqual(result["meta"]["count"], 1)


class CopyBaselineTests(ApiTest):
    def setUp(self):
        super(CopyBaselineTests, self).setUp()
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
        super(CopyBaselineTests, self).tearDown()
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
            "api/system-baseline/v1/baselines/%s?display_name=" % source_uuid,
            headers=fixtures.AUTH_HEADER,
        )
        self.assertEqual(response.status_code, 400)

        response = self.client.post(
            "api/system-baseline/v1/baselines/%s?display_name=copy" % source_uuid,
            headers=fixtures.AUTH_HEADER,
        )
        self.assertEqual(response.status_code, 200)
        copied_baseline = json.loads(response.data)

        response = self.client.post(
            "api/system-baseline/v1/baselines/%s?display_name=copy" % source_uuid,
            headers=fixtures.AUTH_HEADER,
        )
        self.assertEqual(response.status_code, 400)

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


class ApiPatchTests(ApiTest):
    def setUp(self):
        super(ApiPatchTests, self).setUp()
        self.client.post(
            "api/system-baseline/v1/baselines",
            headers=fixtures.AUTH_HEADER,
            json=fixtures.BASELINE_THREE_LOAD,
        )

    def tearDown(self):
        super(ApiPatchTests, self).tearDown()
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

        # attempt to use an empty fact name
        response = self.client.patch(
            "api/system-baseline/v1/baselines/%s" % patched_uuid,
            headers=fixtures.AUTH_HEADER,
            json=fixtures.BASELINE_PATCH_EMPTY_NAME,
        )
        self.assertIn("fact name cannot be empty", response.data.decode("utf-8"))
        self.assertEqual(response.status_code, 400)

        # attempt to use an empty fact value
        response = self.client.patch(
            "api/system-baseline/v1/baselines/%s" % patched_uuid,
            headers=fixtures.AUTH_HEADER,
            json=fixtures.BASELINE_PATCH_EMPTY_VALUE,
        )
        self.assertIn(
            "value for cpu_sockets_renamed cannot be empty",
            response.data.decode("utf-8"),
        )
        # attempt to rename the baseline to a bad name
        response = self.client.patch(
            "api/system-baseline/v1/baselines/%s" % patched_uuid,
            headers=fixtures.AUTH_HEADER,
            json=fixtures.BASELINE_PATCH_LONG_NAME,
        )
        self.assertEqual(response.status_code, 400)

        # attempt to add a fact with leading whitespace
        response = self.client.patch(
            "api/system-baseline/v1/baselines/%s" % patched_uuid,
            headers=fixtures.AUTH_HEADER,
            json=fixtures.BASELINE_PATCH_LEADING_WHITESPACE_NAME,
        )
        self.assertEqual(response.status_code, 400)

        # attempt to add a fact with trailing whitespace
        response = self.client.patch(
            "api/system-baseline/v1/baselines/%s" % patched_uuid,
            headers=fixtures.AUTH_HEADER,
            json=fixtures.BASELINE_PATCH_TRAILING_WHITESPACE_NAME,
        )
        self.assertEqual(response.status_code, 400)

        # attempt to add a value with leading whitespace
        response = self.client.patch(
            "api/system-baseline/v1/baselines/%s" % patched_uuid,
            headers=fixtures.AUTH_HEADER,
            json=fixtures.BASELINE_PATCH_LEADING_WHITESPACE_VALUE,
        )
        self.assertEqual(response.status_code, 400)

        # attempt to add a value with trailing whitespace
        response = self.client.patch(
            "api/system-baseline/v1/baselines/%s" % patched_uuid,
            headers=fixtures.AUTH_HEADER,
            json=fixtures.BASELINE_PATCH_TRAILING_WHITESPACE_VALUE,
        )
        self.assertEqual(response.status_code, 400)


class CreateFromInventoryTests(ApiTest):
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
        super(CreateFromInventoryTests, self).tearDown()

    @patch("system_baseline.views.v1.fetch_systems_with_profiles")
    def test_create_from_inventory(self, mock_fetch):
        mock_fetch.return_value = [fixtures.SYSTEM_WITH_PROFILE]
        response = self.client.post(
            "api/system-baseline/v1/baselines",
            headers=fixtures.AUTH_HEADER,
            json=fixtures.CREATE_FROM_INVENTORY,
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            "api/system-baseline/v1/baselines",
            headers=fixtures.AUTH_HEADER,
            json=fixtures.CREATE_FROM_INVENTORY_LONG_NAME,
        )
        self.assertEqual(response.status_code, 400)

    @patch("system_baseline.views.v1.fetch_systems_with_profiles")
    def test_create_from_inventory_not_found(self, mock_fetch):
        mock_fetch.side_effect = ItemNotReturned("not found!")
        response = self.client.post(
            "api/system-baseline/v1/baselines",
            headers=fixtures.AUTH_HEADER,
            json=fixtures.CREATE_FROM_INVENTORY,
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            "inventory UUID df925152-c45d-11e9-a1f0-c85b761454fa not available",
            response.data.decode("utf-8"),
        )

    def test_create_from_inventory_bad_uuid(self):
        response = self.client.post(
            "api/system-baseline/v1/baselines",
            headers=fixtures.AUTH_HEADER,
            json=fixtures.CREATE_FROM_INVENTORY_MALFORMED_UUID,
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("malformed UUIDs requested", response.data.decode("utf-8"))


class ApiDuplicateTests(ApiTest):
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
        super(ApiDuplicateTests, self).tearDown()

    def test_duplicate_baseline(self):
        response = self.client.post(
            "api/system-baseline/v1/baselines",
            headers=fixtures.AUTH_HEADER,
            json=fixtures.BASELINE_DUPLICATES_LOAD,
        )
        self.assertIn(
            "name nested_cpu_sockets declared more than once",
            response.data.decode("utf-8"),
        )

        response = self.client.post(
            "api/system-baseline/v1/baselines",
            headers=fixtures.AUTH_HEADER,
            json=fixtures.BASELINE_DUPLICATES_TWO_LOAD,
        )
        self.assertIn("memory declared more than once", response.data.decode("utf-8"))

        response = self.client.post(
            "api/system-baseline/v1/baselines",
            headers=fixtures.AUTH_HEADER,
            json=fixtures.BASELINE_DUPLICATES_THREE_LOAD,
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("memory declared more than once", response.data.decode("utf-8"))

    def test_create_baseline_with_leading_trailing_whitespace(self):
        response = self.client.post(
            "api/system-baseline/v1/baselines",
            headers=fixtures.AUTH_HEADER,
            json=fixtures.BASELINE_NAME_LEADING_WHITESPACE,
        )
        self.assertEqual(response.status_code, 400)

        response = self.client.post(
            "api/system-baseline/v1/baselines",
            headers=fixtures.AUTH_HEADER,
            json=fixtures.BASELINE_NAME_TRAILING_WHITESPACE,
        )
        self.assertEqual(response.status_code, 400)
