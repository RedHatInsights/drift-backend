import csv
import json
import logging
from io import StringIO

from drift import app
from kerlescan.exceptions import ServiceError, ItemNotReturned

from . import fixtures
import mock
import unittest


class ApiTests(unittest.TestCase):
    def setUp(self):
        test_connexion_app = app.create_app()
        test_flask_app = test_connexion_app.app
        self.client = test_flask_app.test_client()

    def test_comparison_report_api_no_args_or_header(self):
        response = self.client.get("api/drift/v1/comparison_report")
        self.assertEqual(response.status_code, 400)

    def test_comparison_report_api_no_header(self):
        response = self.client.get(
            "api/drift/v1/comparison_report?"
            "system_ids[]=d6bba69a-25a8-11e9-81b8-c85b761454fa"
            "system_ids[]=11b3cbce-25a9-11e9-8457-c85b761454fa"
        )
        self.assertEqual(response.status_code, 400)

    def test_comparison_report_api_post(self):
        data = {
            "system_ids": [
                "d6bba69a-25a8-11e9-81b8-c85b761454fa",
                "11b3cbce-25a9-11e9-8457-c85b761454fa",
            ]
        }
        response = self.client.post("api/drift/v1/comparison_report", data=data)
        self.assertEqual(response.status_code, 400)

    def test_compare_api_no_account_number(self):
        response = self.client.get(
            "api/drift/v1/comparison_report?"
            "system_ids[]=d6bba69a-25a8-11e9-81b8-c85b761454fa"
            "&system_ids[]=11b3cbce-25a9-11e9-8457-c85b761454fa",
            headers=fixtures.AUTH_HEADER_NO_ACCT,
        )
        self.assertEqual(response.status_code, 400)

    # this scenario should never happen in real life
    def test_compare_api_no_account_number_but_has_ents(self):
        response = self.client.get(
            "api/drift/v1/comparison_report?"
            "system_ids[]=d6bba69a-25a8-11e9-81b8-c85b761454fa"
            "&system_ids[]=11b3cbce-25a9-11e9-8457-c85b761454fa",
            headers=fixtures.AUTH_HEADER_NO_ACCT_BUT_HAS_ENTS,
        )
        self.assertEqual(response.status_code, 400)

    def test_compare_api_no_entitlement(self):
        response = self.client.get(
            "api/drift/v1/comparison_report?"
            "system_ids[]=d6bba69a-25a8-11e9-81b8-c85b761454fa"
            "&system_ids[]=11b3cbce-25a9-11e9-8457-c85b761454fa",
            headers=fixtures.AUTH_HEADER_SMART_MGMT_FALSE,
        )
        self.assertEqual(response.status_code, 400)

    def test_comparison_report_duplicate_uuid(self):
        response = self.client.get(
            "api/drift/v1/comparison_report?"
            "system_ids[]=d6bba69a-25a8-11e9-81b8-c85b761454fa"
            "&system_ids[]=d6bba69a-25a8-11e9-81b8-c85b761454fa",
            headers=fixtures.AUTH_HEADER,
        )
        self.assertEqual(response.status_code, 400)

    def test_comparison_report_bad_uuid(self):
        response = self.client.get(
            "api/drift/v1/comparison_report?"
            "system_ids[]=d6bba69a-25a8-11e9-81b8-c85b761454faaaaaa"
            "&system_ids[]=d6bba69a-25a8-11e9-81b8-c85b761454fa",
            headers=fixtures.AUTH_HEADER,
        )
        self.assertEqual(response.status_code, 400)

    @mock.patch("drift.views.v1.fetch_systems_with_profiles")
    def test_comparison_report_api(self, mock_fetch_systems):
        mock_fetch_systems.return_value = fixtures.FETCH_SYSTEMS_WITH_PROFILES_RESULT
        response = self.client.get(
            "api/drift/v1/comparison_report?"
            "system_ids[]=d6bba69a-25a8-11e9-81b8-c85b761454fa"
            "&system_ids[]=11b3cbce-25a9-11e9-8457-c85b761454fa",
            headers=fixtures.AUTH_HEADER,
        )
        self.assertEqual(response.status_code, 200)
        comparisons = json.loads(response.data)
        # we hard-code the index lookup since we know the fixture layout
        network_comparisons = comparisons["facts"][12]["comparisons"]
        ipv4_comparison = [
            comparison
            for comparison in network_comparisons
            if comparison["name"] == "eth99.ipv4_addresses"
        ][0]
        self.assertEqual(ipv4_comparison["state"], "DIFFERENT")

        ipv6_comparison = [
            comparison
            for comparison in network_comparisons
            if comparison["name"] == "eth99.ipv6_addresses"
        ][0]
        self.assertEqual(ipv6_comparison["state"], "DIFFERENT")

        fqdn_comparison = comparisons["facts"][7]
        self.assertEqual(fqdn_comparison["name"], "fqdn")
        self.assertEqual(fqdn_comparison["state"], "DIFFERENT")

        fqdn_comparison = comparisons["facts"][11]
        self.assertEqual(fqdn_comparison["name"], "last_boot_time")
        self.assertEqual(fqdn_comparison["state"], "INCOMPLETE_DATA")

    @mock.patch("drift.views.v1.fetch_systems_with_profiles")
    def test_comparison_report_api_csv(self, mock_fetch_systems):
        mock_fetch_systems.return_value = fixtures.FETCH_SYSTEMS_WITH_PROFILES_RESULT
        response = self.client.get(
            "api/drift/v1/comparison_report?"
            "system_ids[]=d6bba69a-25a8-11e9-81b8-c85b761454fa"
            "&system_ids[]=11b3cbce-25a9-11e9-8457-c85b761454fa",
            headers={**fixtures.AUTH_HEADER, "Accept": "text/csv"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["Content-type"], "text/csv")
        csv_data = StringIO(response.data.decode("ascii"))
        reader = csv.DictReader(csv_data)
        self.assertEqual(
            [
                "name",
                "state",
                "fake_system_99.example.com",
                "hostname_one",
                "hostname_one",
            ],
            reader.fieldnames,
        )

    @mock.patch("drift.views.v1.fetch_baselines")
    @mock.patch("drift.views.v1.fetch_systems_with_profiles")
    def test_comparison_report_api_baselines(
        self, mock_fetch_systems, mock_fetch_baselines
    ):
        mock_fetch_systems.return_value = fixtures.FETCH_SYSTEMS_WITH_PROFILES_RESULT
        mock_fetch_baselines.return_value = fixtures.FETCH_BASELINES_RESULT
        response = self.client.get(
            "api/drift/v1/comparison_report?"
            "system_ids[]=d6bba69a-25a8-11e9-81b8-c85b761454fa"
            "&system_ids[]=11b3cbce-25a9-11e9-8457-c85b761454fa"
            "&baseline_ids[]=ff35596c-f98e-11e9-aea9-98fa9b07d419"
            "&baseline_ids[]=89df6310-f98e-11e9-8a65-98fa9b07d419",
            headers=fixtures.AUTH_HEADER,
        )
        self.assertEqual(response.status_code, 200)

        returned_comparisons = json.loads(response.data)["facts"]
        returned_fact_names = set(x["name"] for x in returned_comparisons)
        self.assertNotIn("name", returned_fact_names)
        self.assertEquals("", returned_comparisons[0]["systems"][0]["value"])

    @mock.patch("drift.views.v1.fetch_systems_with_profiles")
    def test_comparison_report_api_same_facts(self, mock_fetch_systems):
        mock_fetch_systems.return_value = (
            fixtures.FETCH_SYSTEMS_WITH_PROFILES_SAME_FACTS_RESULT
        )
        response = self.client.get(
            "api/drift/v1/comparison_report?"
            "system_ids[]=d6bba69a-25a8-11e9-81b8-c85b761454fa"
            "&system_ids[]=11b3cbce-25a9-11e9-8457-c85b761454fa",
            headers=fixtures.AUTH_HEADER,
        )
        self.assertEqual(response.status_code, 200)

    @mock.patch("drift.views.v1.fetch_systems_with_profiles")
    def test_comparison_report_api_missing_system_uuid(self, mock_fetch_systems):
        mock_fetch_systems.side_effect = ItemNotReturned("oops")
        response = self.client.get(
            "api/drift/v1/comparison_report?"
            "system_ids[]=d6bba69a-25a8-11e9-81b8-c85b761454fa"
            "&system_ids[]=11b3cbce-25a9-11e9-8457-c85b761454fa",
            headers=fixtures.AUTH_HEADER,
        )
        self.assertEqual(response.status_code, 400)

    @mock.patch("drift.views.v1.fetch_systems_with_profiles")
    def test_comparison_report_api_500_backend(self, mock_fetch_systems):
        mock_fetch_systems.side_effect = ServiceError("oops")
        response = self.client.get(
            "api/drift/v1/comparison_report?"
            "system_ids[]=d6bba69a-25a8-11e9-81b8-c85b761454fa"
            "&system_ids[]=11b3cbce-25a9-11e9-8457-c85b761454fa",
            headers=fixtures.AUTH_HEADER,
        )
        self.assertEqual(response.status_code, 500)


class DebugLoggingApiTests(unittest.TestCase):
    def setUp(self):
        test_connexion_app = app.create_app()
        test_flask_app = test_connexion_app.app
        self.client = test_flask_app.test_client()

        self.stream = StringIO()
        self.handler = logging.StreamHandler(self.stream)
        test_flask_app.logger.addHandler(self.handler)
        test_flask_app.logger.setLevel(logging.DEBUG)

    @mock.patch("drift.views.v1.get_key_from_headers")
    def test_username_logging_on_debug_no_key(self, mock_get_key):
        mock_get_key.return_value = None
        self.client.get("api/drift/v1/comparison_report")
        self.handler.flush()
        self.assertIn("identity header not sent for request", self.stream.getvalue())
        self.assertNotIn("username from identity header", self.stream.getvalue())

    @mock.patch("kerlescan.view_helpers.get_key_from_headers")
    def test_username_logging_on_debug_with_key(self, mock_get_key):
        mock_get_key.return_value = fixtures.AUTH_HEADER["X-RH-IDENTITY"]
        self.client.get("api/drift/v1/comparison_report")
        self.handler.flush()
        self.assertNotIn("identity header not sent for request", self.stream.getvalue())
        self.assertIn(
            "username from identity header: test_user", self.stream.getvalue()
        )
