import unittest
import responses
from mock import MagicMock as mm

from kerlescan import service_interface
from kerlescan.exceptions import IllegalHttpMethodError


class FetchUrlTests(unittest.TestCase):
    @responses.activate
    def test_http_call(self):
        url = "http://example.com/api/123"
        auth_header = {}
        logger = mm()
        time_metric = mm()
        exception_metric = mm()
        method = "get"

        service_interface._validate_service_response = mm()

        responses.add(
            **{
                "method": responses.GET,
                "url": url,
                "body": '{"result": "called the http"}',
                "status": 200,
                "content_type": "application/json",
                "adding_headers": {"X-Foo": "Bar"},
            }
        )

        result = service_interface.fetch_url(
            url, auth_header, logger, time_metric, exception_metric, method
        )
        self.assertEqual(result, {"result": "called the http"})

    def test_invalid_http_method(self):
        url = "http://example.com/api/123"
        auth_header = {}
        logger = mm()
        time_metric = mm()
        exception_metric = mm()
        method = "invalid_method"

        service_interface._validate_service_response = mm()

        with self.assertRaises(IllegalHttpMethodError):
            service_interface.fetch_url(
                url, auth_header, logger, time_metric, exception_metric, method
            )
