from drift import app
import json

from . import fixtures
import mock
import unittest


class ApiTests(unittest.TestCase):

    def setUp(self):
        test_connexion_app = app.create_app()
        test_flask_app = test_connexion_app.app
        self.client = test_flask_app.test_client()

    def test_status_api_pass(self):
        response = self.client.get("r/insights/platform/drift/v0/status")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data), {'status': 'running'})

    def test_compare_api_no_args_or_header(self):
        response = self.client.get("r/insights/platform/drift/v0/compare")
        self.assertEqual(response.status_code, 400)

    def test_compare_api_no_header(self):
        response = self.client.get("r/insights/platform/drift/v0/compare?"
                                   "host_ids[]=d6bba69a-25a8-11e9-81b8-c85b761454fa"
                                   "host_ids[]=11b3cbce-25a9-11e9-8457-c85b761454fa")
        self.assertEqual(response.status_code, 400)

    @mock.patch('drift.views.v0.fetch_hosts')
    def test_compare_api(self, mock_fetch_hosts):
        mock_fetch_hosts.return_value = fixtures.FETCH_HOSTS_RESULT
        response = self.client.get("r/insights/platform/drift/v0/compare?"
                                   "host_ids[]=d6bba69a-25a8-11e9-81b8-c85b761454fa"
                                   "host_ids[]=11b3cbce-25a9-11e9-8457-c85b761454fa",
                                   headers=fixtures.AUTH_HEADER)
        self.assertEqual(response.status_code, 200)
