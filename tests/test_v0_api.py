from io import StringIO
import logging

from drift import app
from drift.exceptions import InventoryServiceError, SystemNotReturned

from . import fixtures
import mock
import unittest


class ApiTests(unittest.TestCase):

    def setUp(self):
        test_connexion_app = app.create_app()
        test_flask_app = test_connexion_app.app
        self.client = test_flask_app.test_client()

    def test_comparison_report_api_no_args_or_header(self):
        response = self.client.get("r/insights/platform/drift/v0/comparison_report")
        self.assertEqual(response.status_code, 400)

    def test_comparison_report_api_no_header(self):
        response = self.client.get("r/insights/platform/drift/v0/comparison_report?"
                                   "system_ids[]=d6bba69a-25a8-11e9-81b8-c85b761454fa"
                                   "system_ids[]=11b3cbce-25a9-11e9-8457-c85b761454fa")
        self.assertEqual(response.status_code, 400)

    def test_compare_api_no_account_number(self):
        response = self.client.get("r/insights/platform/drift/v0/compare?"
                                   "system_ids[]=d6bba69a-25a8-11e9-81b8-c85b761454fa"
                                   "&system_ids[]=11b3cbce-25a9-11e9-8457-c85b761454fa",
                                   headers=fixtures.AUTH_HEADER_NO_ACCT)
        self.assertEqual(response.status_code, 400)

    def test_comparison_report_duplicate_uuid(self):
        response = self.client.get("r/insights/platform/drift/v0/comparison_report?"
                                   "system_ids[]=d6bba69a-25a8-11e9-81b8-c85b761454fa"
                                   "&system_ids[]=d6bba69a-25a8-11e9-81b8-c85b761454fa",
                                   headers=fixtures.AUTH_HEADER)
        self.assertEqual(response.status_code, 400)

    @mock.patch('drift.views.v0.fetch_systems')
    def test_comparison_report_api(self, mock_fetch_systems):
        mock_fetch_systems.return_value = fixtures.FETCH_SYSTEMS_RESULT
        response = self.client.get("r/insights/platform/drift/v0/comparison_report?"
                                   "system_ids[]=d6bba69a-25a8-11e9-81b8-c85b761454fa"
                                   "&system_ids[]=11b3cbce-25a9-11e9-8457-c85b761454fa",
                                   headers=fixtures.AUTH_HEADER)
        self.assertEqual(response.status_code, 200)

    @mock.patch('drift.views.v0.fetch_systems')
    def test_comparison_report_api_same_facts(self, mock_fetch_systems):
        mock_fetch_systems.return_value = fixtures.FETCH_SYSTEMS_SAME_FACTS_RESULT
        response = self.client.get("r/insights/platform/drift/v0/comparison_report?"
                                   "system_ids[]=d6bba69a-25a8-11e9-81b8-c85b761454fa"
                                   "&system_ids[]=11b3cbce-25a9-11e9-8457-c85b761454fa",
                                   headers=fixtures.AUTH_HEADER)
        self.assertEqual(response.status_code, 200)

    @mock.patch('drift.views.v0.config')
    @mock.patch('drift.views.v0.fetch_systems')
    def test_comparison_report_api_mock_facts(self, mock_fetch_systems, mock_config):
        mock_config.inventory_svc_hostname = "http://inventory_svc_url_is_not_set"
        mock_config.return_mock_data = True
        mock_fetch_systems.return_value = fixtures.FETCH_SYSTEMS_RESULT

        response = self.client.get("r/insights/platform/drift/v0/comparison_report?"
                                   "system_ids[]=d6bba69a-25a8-11e9-81b8-c85b761454fa"
                                   "&system_ids[]=11b3cbce-25a9-11e9-8457-c85b761454fa",
                                   headers=fixtures.AUTH_HEADER)
        self.assertEqual(response.status_code, 200)

    @mock.patch('drift.views.v0.fetch_systems')
    def test_comparison_report_api_missing_system_uuid(self, mock_fetch_systems):
        mock_fetch_systems.side_effect = SystemNotReturned("oops")
        response = self.client.get("r/insights/platform/drift/v0/comparison_report?"
                                   "system_ids[]=d6bba69a-25a8-11e9-81b8-c85b761454fa"
                                   "&system_ids[]=11b3cbce-25a9-11e9-8457-c85b761454fa",
                                   headers=fixtures.AUTH_HEADER)
        self.assertEqual(response.status_code, 400)

    @mock.patch('drift.views.v0.fetch_systems')
    def test_comparison_report_api_500_backend(self, mock_fetch_systems):
        mock_fetch_systems.side_effect = InventoryServiceError("oops")
        response = self.client.get("r/insights/platform/drift/v0/comparison_report?"
                                   "system_ids[]=d6bba69a-25a8-11e9-81b8-c85b761454fa"
                                   "&system_ids[]=11b3cbce-25a9-11e9-8457-c85b761454fa",
                                   headers=fixtures.AUTH_HEADER)
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

    @mock.patch('drift.views.v0.get_key_from_headers')
    def test_username_logging_on_debug_no_key(self, mock_get_key):
        mock_get_key.return_value = None
        self.client.get("r/insights/platform/drift/v0/status")
        self.handler.flush()
        self.assertIn("identity header not sent for request", self.stream.getvalue())
        self.assertNotIn("username from identity header", self.stream.getvalue())

    @mock.patch('drift.views.v0.get_key_from_headers')
    def test_username_logging_on_debug_with_key(self, mock_get_key):
        mock_get_key.return_value = fixtures.AUTH_HEADER['X-RH-IDENTITY']
        self.client.get("r/insights/platform/drift/v0/status")
        self.handler.flush()
        self.assertNotIn("identity header not sent for request", self.stream.getvalue())
        self.assertIn("username from identity header: test_user", self.stream.getvalue())
