from flask import Blueprint, jsonify, request, current_app
from http import HTTPStatus
from uuid import UUID

from drift import info_parser, metrics, app_config
from drift.baseline_service_interface import fetch_baselines

from kerlescan import view_helpers
from kerlescan.inventory_service_interface import fetch_systems_with_profiles
from kerlescan.service_interface import get_key_from_headers
from kerlescan.exceptions import HTTPError, ItemNotReturned

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
                HTTPStatus.BAD_REQUEST, message="%s is not a UUID" % system_id
            )


def get_event_counters():
    """
    small helper to create a dict of event counters
    """
    return {
        "systems_compared_no_sysprofile": metrics.systems_compared_no_sysprofile,
        "inventory_service_requests": metrics.inventory_service_requests,
        "inventory_service_exceptions": metrics.inventory_service_exceptions,
    }


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
    _validate_uuids(baseline_ids)

    try:
        comparisons = info_parser.build_comparisons(
            fetch_systems_with_profiles(
                system_ids, auth_key, current_app.logger, get_event_counters()
            ),
            fetch_baselines(baseline_ids, auth_key, current_app.logger),
        )
        metrics.systems_compared.observe(len(system_ids))
        return jsonify(comparisons)
    except ItemNotReturned as error:
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


@section.before_app_request
def log_username():
    view_helpers.log_username(current_app.logger, request)


@section.before_app_request
def ensure_entitled():
    return view_helpers.ensure_entitled(
        request, app_config.get_app_name(), current_app.logger
    )


@section.before_app_request
def ensure_account_number():
    return view_helpers.ensure_account_number(request, current_app.logger)
