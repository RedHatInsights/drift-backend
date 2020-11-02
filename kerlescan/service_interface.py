import requests

from kerlescan.constants import AUTH_HEADER_NAME
from kerlescan.exceptions import ServiceError, ItemNotReturned, RBACDenied


def get_key_from_headers(incoming_headers):
    """
    return auth key from header
    """
    return incoming_headers.get(AUTH_HEADER_NAME)


def _validate_service_response(response, logger):
    """
    Raise an exception if the response was not what we expected.
    """
    if response.status_code == requests.codes.not_found:
        logger.info(
            "%s error received from service: %s" % (response.status_code, response.text)
        )
        raise ItemNotReturned(response.text)

    if response.status_code == requests.codes.forbidden:
        logger.info(
            "%s error received from service: %s" % (response.status_code, response.text)
        )
        raise RBACDenied(response.text)

    if response.status_code != requests.codes.ok:
        logger.warn(
            "%s error received from service: %s" % (response.status_code, response.text)
        )
        raise ServiceError("Error received from backend service")


def fetch_url(url, auth_header, logger, time_metric, exception_metric):
    """
    helper to make a single request
    """
    logger.debug("fetching %s" % url)
    with time_metric.time():
        with exception_metric.count_exceptions():
            response = requests.get(url, headers=auth_header)
    logger.debug("fetched %s" % url)
    _validate_service_response(response, logger)
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
            url % (", ".join(object_id_batch)),
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
