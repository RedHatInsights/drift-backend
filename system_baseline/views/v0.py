from flask import Blueprint, request, current_app
from http import HTTPStatus
import logging
import json
import base64

from system_baseline import metrics
from system_baseline.constants import AUTH_HEADER_NAME
from system_baseline.exceptions import HTTPError

section = Blueprint("v0", __name__)

BASELINES = {
    "total": 2,
    "count": 2,
    "page": 1,
    "per_page": 50,
    "results": [
        {
            "id": "1234",
            "display_name": "beav's baseline",
            "fact_count": 2,
            "created": "2019-01-18T13:30:00.000000Z",
            "updated": "2019-05-18T15:00:00.000000Z",
        },
        {
            "id": "abcd",
            "display_name": "micjohns' baseline",
            "fact_count": 2,
            "created": "2019-02-18T13:30:00.000000Z",
            "updated": "2019-05-19T15:00:00.000000Z",
        },
    ],
}

BASELINE_MICJOHNS = {
    "id": "abcd",
    "display_name": "micjohns' baseline",
    "fact_count": 2,
    "created": "2019-02-18T13:30:00.000000Z",
    "updated": "2019-05-19T15:00:00.000000Z",
    "baseline_facts": {
        "arch": "x86_64",
        "cloud_provider": "stratosphere of Neptune",
        "mountains": "dislike",
    },
}

BASELINE_BEAV = {
    "id": "1234",
    "display_name": "beav's baseline",
    "fact_count": 2,
    "created": "2019-01-18T13:30:00.000000Z",
    "updated": "2019-05-18T15:00:00.000000Z",
    "baseline_facts": {"arch": "x86_64", "cloud_provider": "tiny ice crystals"},
}


@metrics.api_exceptions.count_exceptions()
def get_baselines_by_ids(baseline_ids):
    """
    return a list of baseline objects
    """
    fetched_baselines = []

    for baseline_id in baseline_ids:
        # validate that we have all IDs requested
        if baseline_id == "1234":
            fetched_baselines.append(BASELINE_BEAV)
        elif baseline_id == "abcd":
            fetched_baselines.append(BASELINE_MICJOHNS)
        else:
            raise HTTPError(HTTPStatus.NOT_FOUND, message="ID not found")

    # assemble metadata
    response = {
        "total": len(fetched_baselines),
        "count": len(fetched_baselines),
        "page": 1,
        "per_page": 50,
        "results": fetched_baselines,
    }

    return response


@metrics.api_exceptions.count_exceptions()
def get_baseline_ids():
    """
    return a list of available objects
    """
    return BASELINES


def _is_mgmt_url(path):
    """
    small helper to test if URL is for management API.
    """
    return path.startswith("/mgmt/")


def _is_openapi_url(path):
    """
    small helper to test if URL is the openapi spec
    """
    return path == "/api/system_baseline/v0/openapi.json"


@section.before_app_request
def ensure_account_number():
    auth_key = get_key_from_headers(request.headers)
    if auth_key:
        identity = json.loads(base64.b64decode(auth_key))["identity"]
        if "account_number" not in identity:
            current_app.logger.debug(
                "account number not found on identity token %s" % auth_key
            )
            raise HTTPError(
                HTTPStatus.BAD_REQUEST,
                message="account number not found on identity token",
            )


@section.before_app_request
def ensure_entitled():
    """
    check if the request is entitled. We run this on all requests and bail out
    if the URL is whitelisted. Returning 'None' allows the request to go through.
    """
    # TODO: Blueprint.before_request was not working as expected, using
    # before_app_request and checking URL here instead.
    if _is_mgmt_url(request.path) or _is_openapi_url(request.path):
        return  # allow request

    auth_key = get_key_from_headers(request.headers)
    if auth_key:
        entitlements = json.loads(base64.b64decode(auth_key)).get("entitlements", {})
        if "smart_management" in entitlements:
            if entitlements["smart_management"].get("is_entitled"):
                current_app.logger.debug(
                    "enabled smart management entitlement found on header"
                )
                return  # allow request
    else:
        current_app.logger.debug("identity header not sent for request")

    # if we got here, reject the request
    current_app.logger.debug("smart management entitlement not found for account.")
    raise HTTPError(
        HTTPStatus.BAD_REQUEST,
        message="Smart management entitlement not found for account.",
    )


@section.before_app_request
def log_username():
    if current_app.logger.level == logging.DEBUG:
        auth_key = get_key_from_headers(request.headers)
        if auth_key:
            identity = json.loads(base64.b64decode(auth_key))["identity"]
            current_app.logger.debug(
                "username from identity header: %s" % identity["user"]["username"]
            )
        else:
            current_app.logger.debug("identity header not sent for request")


def get_key_from_headers(incoming_headers):
    """
    return auth key from header
    """
    return incoming_headers.get(AUTH_HEADER_NAME)
