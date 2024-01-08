import requests

from kerlescan.config import drift_shared_secret, tls_ca_path
from kerlescan.constants import AUTH_HEADER_NAME, DRIFT_INTERNAL_API_HEADER_NAME, VALID_HTTP_VERBS
from kerlescan.exceptions import IllegalHttpMethodError, ItemNotReturned, RBACDenied, ServiceError


def get_key_from_headers(incoming_headers):
    """
    return auth key from header
    """
    return incoming_headers.get(AUTH_HEADER_NAME)


def internal_auth_header():
    """
    returns drift internal header with shared secret
    """
    return {DRIFT_INTERNAL_API_HEADER_NAME: drift_shared_secret}


def _validate_service_response(response, logger, auth_header):
    """
    Raise an exception if the response was not what we expected.
    """
    if response.status_code == requests.codes.not_found:
        logger.info("%s error received from service: %s" % (response.status_code, response.text))
        raise ItemNotReturned(response.text)

    if response.status_code in [requests.codes.forbidden, requests.codes.unauthorized]:
        logger.info("%s error received from service: %s" % (response.status_code, response.text))
        # Log identity header if 401 (unauthorized)
        if response.status_code == requests.codes.unauthorized:
            if isinstance(auth_header, dict) and AUTH_HEADER_NAME in auth_header:
                logger.info("identity '%s'" % get_key_from_headers(auth_header))
            else:
                logger.info("no identity or no key")
        raise RBACDenied(response.text)

    if response.status_code != requests.codes.ok:
        logger.warn("%s error received from service: %s" % (response.status_code, response.text))
        raise ServiceError("Error received from backend service")


def fetch_url(url, auth_header, logger, time_metric, exception_metric, method="get", json=None):
    """
    helper to make a single request
    """

    if method not in VALID_HTTP_VERBS:
        raise IllegalHttpMethodError("Provided method '%s' is not valid HTTP method." % method)

    logger.debug("fetching %s" % url)
    with time_metric.time():
        with exception_metric.count_exceptions():
            response = requests.request(
                method, url, headers=auth_header, verify=tls_ca_path, json=json
            )
    logger.debug("fetched %s" % url)
    _validate_service_response(response, logger, auth_header)
    return response.json()


def fetch_data(url, auth_header, object_ids, logger, time_metric, exception_metric):
    """
    fetch objects based on ID in batches of 40 for given RESTful URL

    A batch size of 40 was chosen to fetch as many items per request as we
    can, but still keep some headroom in the URL length.
    """
    BATCH_SIZE = 40
    # tags API call returns a dict in "results", so we now
    # need to handle either dict or list/array in "results"
    result_list = []
    result_dict = {}
    object_ids_to_fetch = object_ids

    while len(object_ids_to_fetch) > 0:
        object_id_batch = object_ids_to_fetch[:BATCH_SIZE]
        response_json = fetch_url(
            url % (",".join(object_id_batch)),
            auth_header,
            logger,
            time_metric,
            exception_metric,
        )
        # older APIs sent data in "results", newer uses "data"
        if "data" in response_json:
            result = response_json["data"]
        elif "results" in response_json:
            result = response_json["results"]
        else:
            raise ServiceError("unparsable result returned from service")
        if isinstance(result, dict):
            result_dict.update(result)
        else:
            result_list += result
        object_ids_to_fetch = object_ids_to_fetch[BATCH_SIZE:]

    results = result_dict if result_dict else result_list
    return results
