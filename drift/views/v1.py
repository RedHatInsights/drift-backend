from flask import Blueprint, jsonify, request, current_app
from http import HTTPStatus
import logging
import json
import base64
from uuid import UUID

from drift import info_parser, metrics
from drift.exceptions import HTTPError, SystemNotReturned
from drift.inventory_service_interface import fetch_systems_with_profiles
from drift.service_interface import get_key_from_headers
from drift.baseline_service_interface import fetch_baselines

section = Blueprint("v1", __name__)


def _validate_uuids(system_ids):
    """
    helper method to test if a UUID is properly formatted. Will raise an
    exception if format is wrong.
    """
    for system_id in system_ids:
        try:
            UUID(system_id)
        except ValueError:
            raise HTTPError(
                HTTPStatus.BAD_REQUEST, message="system_id %s is not a UUID" % system_id
            )


def comparison_report(system_ids, baseline_ids, auth_key):
    """
    return a comparison report
    """
    if len(system_ids) > len(set(system_ids)):
        raise HTTPError(
            HTTPStatus.BAD_REQUEST,
            message="duplicate UUID specified in system_ids list",
        )

    _validate_uuids(system_ids)

    try:
        comparisons = info_parser.build_comparisons(
            fetch_systems_with_profiles(system_ids, auth_key, current_app.logger),
            fetch_baselines(baseline_ids, auth_key, current_app.logger),
        )
        metrics.systems_compared.observe(len(system_ids))
        return jsonify(comparisons)
    except SystemNotReturned as error:
        raise HTTPError(HTTPStatus.BAD_REQUEST, message=error.message)


@metrics.comparison_report_requests.time()
@metrics.api_exceptions.count_exceptions()
def comparison_report_get():
    """
    small wrapper over comparison_report for GETs
    """
    system_ids = request.args.getlist("system_ids[]")
    baseline_ids = request.args.getlist("baseline_ids[]")
    auth_key = get_key_from_headers(request.headers)

    return comparison_report(system_ids, baseline_ids, auth_key)


@metrics.comparison_report_requests.time()
@metrics.api_exceptions.count_exceptions()
def comparison_report_post():
    """
    small wrapper over comparison_report for POSTs
    """
    system_ids = request.json["system_ids"]
    baseline_ids = []
    if "baseline_ids" in request.json:
        baseline_ids = request.json["baseline_ids"]
    auth_key = get_key_from_headers(request.headers)

    return comparison_report(system_ids, baseline_ids, auth_key)


def _is_mgmt_url(path):
    """
    small helper to test if URL is for management API.
    """
    return path.startswith("/mgmt/")


def _is_openapi_url(path):
    """
    small helper to test if URL is the openapi spec
    """
    return path == "/api/drift/v1/openapi.json"


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
