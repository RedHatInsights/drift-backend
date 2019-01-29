from drift import app
from requests import RequestException
import json

import mock
import unittest


class ApiTests(unittest.TestCase):

    def setUp(self):
        test_connexion_app = app.create_app()
        test_flask_app = test_connexion_app.app
        self.client = test_flask_app.test_client()

    @mock.patch('requests.get')
    @mock.patch('os.getenv')
    def test_status_api_pass(self, mock_getenv, mock_get):
        mock_inventory_response = mock.Mock()
        mock_inventory_response.status_code = 200
        mock_get.return_value = mock_inventory_response

        mock_getenv.return_value = "http://service.example.com"

        response = self.client.get("r/insights/platform/drift/v0/status")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data),
                         {'status': 'running', 'inventory_connection': 'pass'})

    @mock.patch('requests.get')
    @mock.patch('os.getenv')
    def test_status_api_fail_404(self, mock_getenv, mock_get):
        mock_inventory_response = mock.Mock()
        mock_inventory_response.status_code = 404
        mock_get.return_value = mock_inventory_response

        mock_getenv.return_value = "http://service.example.com"

        response = self.client.get("r/insights/platform/drift/v0/status")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data),
                         {'status': 'running', 'inventory_connection': 'fail'})

    @mock.patch('requests.get')
    @mock.patch('os.getenv')
    def test_status_api_fail_exception(self, mock_getenv, mock_get):
        mock_get.side_effect = RequestException("oops")

        mock_getenv.return_value = "http://service.example.com"

        response = self.client.get("r/insights/platform/drift/v0/status")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data),
                         {'status': 'running', 'inventory_connection': 'fail'})

    def test_compare_api(self):
        response = self.client.get("r/insights/platform/drift/v0/compare")
        self.assertEqual(response.status_code, 200)
