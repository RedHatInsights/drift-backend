import unittest

import mock
import responses

from kerlescan import system_baseline_service_interface as sbsi


class DeletionRequestForSystemsTests(unittest.TestCase):
    @responses.activate
    def test_http_call(self):
        url = (
            "http://baseline_svc_url_is_not_set"
            + "/api/system-baseline/internal/v1/systems/deletion_request"
        )
        system_ids = [1, 2]
        mock_logger = mock.Mock()
        mock_time_metric = mock.MagicMock()
        mock_exception_metric = mock.MagicMock()

        responses.add(
            **{
                "method": responses.POST,
                "url": url,
                "body": '{"result": "called the http"}',
                "status": 200,
                "content_type": "application/json",
                "adding_headers": {"X-Foo": "Bar"},
            }
        )

        result = sbsi.delete_systems_from_notifications(
            system_ids, "test_auth_key", mock_logger, mock_time_metric, mock_exception_metric
        )

        self.assertEqual(result, {"result": "called the http"})
