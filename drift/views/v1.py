import csv
import io

from http import HTTPStatus

from flask import Blueprint, current_app, jsonify, make_response, request
from kerlescan import view_helpers
from kerlescan.exceptions import HTTPError, ItemNotReturned, RBACDenied
from kerlescan.hsp_service_interface import fetch_historical_sys_profiles
from kerlescan.inventory_service_interface import (
    ensure_correct_system_count,
    fetch_systems_with_profiles,
)
from kerlescan.service_interface import get_key_from_headers
from kerlescan.unleash import UNLEASH
from kerlescan.view_helpers import validate_uuids

from drift import app_config, info_parser, metrics
from drift.baseline_service_interface import fetch_baselines
from drift.version import app_version


section = Blueprint("v1", __name__)


def get_version():
    """
    return the service version
    """
    if UNLEASH.is_enabled("version-test"):
        return {"version": "UNLEASH-VERSION"}
    return {"version": app_version}


def get_event_counters():
    """
    small helper to create a dict of event counters
    """
    return {
        "systems_compared_no_sysprofile": metrics.systems_compared_no_sysprofile,
        "inventory_service_requests": metrics.inventory_service_requests,
        "inventory_service_exceptions": metrics.inventory_service_exceptions,
        "hsp_service_requests": metrics.hsp_service_requests,
        "hsp_service_exceptions": metrics.hsp_service_exceptions,
    }


def _csvify(comparisons):
    """
    given a set of comparisons, return a CSV
    """
    # helper methods to generate CSV rows
    def _get_value_for_id(record_id, systems):
        for system in systems:
            if system["id"] == record_id:
                return system["value"]

    def _populate_row(fact, indent=False, group_summary=False):
        if indent:
            row = {"name": "    %s" % fact["name"], "state": fact["state"]}
        else:
            row = {"name": fact["name"], "state": fact["state"]}

        if not group_summary:
            for record_id in record_ids:
                row[record_id] = _get_value_for_id(record_id, fact["systems"])

        return row

    fieldnames = ["name", "state"]
    record_ids = []
    system_names = {}
    # add baselines to the CSV dict, then systems, then historical system profiles
    for baseline in comparisons["baselines"]:
        record_ids.append(baseline["id"])
        system_names[baseline["id"]] = baseline["display_name"]

    for system in comparisons["systems"]:
        record_ids.append(system["id"])
        system_names[system["id"]] = system["display_name"]

    for historical_sys_profile in comparisons["historical_system_profiles"]:
        record_ids.append(historical_sys_profile["id"])
        system_names[historical_sys_profile["id"]] = historical_sys_profile["display_name"]

    output = io.StringIO()
    csvwriter = csv.DictWriter(output, fieldnames=fieldnames + record_ids)
    # write header. We do this manually in order to display system names and not UUIDS.
    csvwriter.writerow({"name": "name", "state": "state", **system_names})

    for fact in comparisons["facts"]:
        if "systems" in fact:
            row = _populate_row(fact)
            csvwriter.writerow(row)
        elif "comparisons" in fact:
            row = _populate_row(fact, group_summary=True)
            csvwriter.writerow(row)
            for comparison in fact["comparisons"]:
                row = _populate_row(comparison, indent=True)
                csvwriter.writerow(row)

    result = output.getvalue()
    message = "CSV written out"
    current_app.logger.audit(message, request=request, success=True)
    output.close()
    return result


PT_CR_API_REQUESTS = metrics.performance_timing.labels(
    method="comparison_report", method_part="api_requests"
)
PT_CR_BUILD_COMPARISON = metrics.performance_timing.labels(
    method="comparison_report", method_part="build_comparison"
)


def comparison_report(
    system_ids,
    baseline_ids,
    historical_sys_profile_ids,
    reference_id,
    auth_key,
    data_format,
    short_circuit,
):
    """
    return a comparison report

    If short_circuit is true, this is a call to see if a single system has
    drifted from a single baseline in order to trigger a Notification if
    necessary, so the only facts that will be compared will be those present
    on the baseline.  If the system has drifted from the baseline, the report
    will contain the key 'drift_event_notify' set to True, otherwise False.
    """
    if len(system_ids + baseline_ids + historical_sys_profile_ids) == 0:
        message = "must specify at least one of system, baseline, or HSP"
        current_app.logger.audit(
            str(HTTPStatus.BAD_REQUEST) + " " + message, request=request, success=False
        )
        raise HTTPError(
            HTTPStatus.BAD_REQUEST,
            message=message,
        )
    if len(system_ids) > len(set(system_ids)):
        message = "duplicate UUID specified in system_ids list"
        current_app.logger.audit(
            str(HTTPStatus.BAD_REQUEST) + " " + message, request=request, success=False
        )
        raise HTTPError(
            HTTPStatus.BAD_REQUEST,
            message=message,
        )

    if len(baseline_ids) > len(set(baseline_ids)):
        message = "duplicate UUID specified in baseline_ids list"
        current_app.logger.audit(
            str(HTTPStatus.BAD_REQUEST) + " " + message, request=request, success=False
        )
        raise HTTPError(
            HTTPStatus.BAD_REQUEST,
            message=message,
        )

    if system_ids:
        validate_uuids(system_ids)
    if baseline_ids:
        validate_uuids(baseline_ids)
    if historical_sys_profile_ids:
        validate_uuids(historical_sys_profile_ids)
    if reference_id:
        validate_uuids([reference_id])
        if reference_id not in (system_ids + baseline_ids + historical_sys_profile_ids):
            message = "reference id %s does not match any ids from query" % reference_id
            current_app.logger.audit(
                str(HTTPStatus.BAD_REQUEST) + " " + message,
                request=request,
                success=False,
            )
            raise HTTPError(
                HTTPStatus.BAD_REQUEST,
                message=message,
            )

    try:
        systems_with_profiles = []
        baseline_results = []
        hsp_results = []

        with PT_CR_API_REQUESTS.time():
            try:
                if system_ids:
                    # can raise RBACDenied exception
                    message = "reading systems with profiles"
                    current_app.logger.audit(message, request=request)
                    systems_with_profiles = fetch_systems_with_profiles(
                        system_ids, auth_key, current_app.logger, get_event_counters()
                    )

                if baseline_ids:
                    # can raise RBACDenied exception
                    message = "reading baselines"
                    current_app.logger.audit(message, request=request)
                    baseline_results = fetch_baselines(baseline_ids, auth_key, current_app.logger)
                    ensure_correct_system_count(baseline_ids, baseline_results)

                if historical_sys_profile_ids:
                    # can raise RBACDenied exception
                    message = "reading historical system profiles"
                    current_app.logger.audit(message, request=request)
                    hsp_results = fetch_historical_sys_profiles(
                        historical_sys_profile_ids,
                        auth_key,
                        current_app.logger,
                        get_event_counters(),
                    )
            except RBACDenied as error:
                message = error.message
                current_app.logger.audit(str(HTTPStatus.FORBIDDEN) + " " + message, request=request)
                raise HTTPError(HTTPStatus.FORBIDDEN, message=message)

        with PT_CR_BUILD_COMPARISON.time():
            comparisons = info_parser.build_comparisons(
                systems_with_profiles,
                baseline_results,
                hsp_results,
                reference_id,
                short_circuit,
            )

        metrics.systems_compared.observe(len(system_ids))
        if data_format == "csv":
            output = make_response(_csvify(comparisons))
            output.headers["Content-Disposition"] = "attachment; filename=export.csv"
            output.headers["Content-type"] = "text/csv"
            return output
        else:
            return jsonify(comparisons)

    except ItemNotReturned as error:
        message = error.message
        current_app.logger.audit(
            str(HTTPStatus.NOT_FOUND) + " " + message, request=request, success=False
        )
        raise HTTPError(HTTPStatus.NOT_FOUND, message=message)


@metrics.comparison_report_requests.time()
@metrics.api_exceptions.count_exceptions()
def comparison_report_get():
    """
    small wrapper over comparison_report for GETs
    """
    system_ids = request.args.getlist("system_ids[]")
    baseline_ids = request.args.getlist("baseline_ids[]")
    historical_sys_profile_ids = request.args.getlist("historical_system_profile_ids[]")
    reference_id = request.args.get("reference_id", None)
    auth_key = get_key_from_headers(request.headers)
    short_circuit = request.args.get("short_circuit", False)

    data_format = "json"
    if "text/csv" in request.headers.get("accept", []):
        data_format = "csv"

    message = "reading comparison report"
    current_app.logger.audit(message, request=request)
    return comparison_report(
        system_ids=system_ids,
        baseline_ids=baseline_ids,
        historical_sys_profile_ids=historical_sys_profile_ids,
        reference_id=reference_id,
        auth_key=auth_key,
        data_format=data_format,
        short_circuit=short_circuit,
    )


@metrics.comparison_report_requests.time()
@metrics.api_exceptions.count_exceptions()
def comparison_report_post():
    """
    small wrapper over comparison_report for POSTs
    """
    system_ids = request.json.get("system_ids", [])
    baseline_ids = request.json.get("baseline_ids", [])
    historical_sys_profile_ids = request.json.get("historical_system_profile_ids", [])
    reference_id = request.json.get("reference_id", None)
    short_circuit = request.args.get("short_circuit", False)

    auth_key = get_key_from_headers(request.headers)

    data_format = "json"
    if "text/csv" in request.headers["accept"]:
        data_format = "csv"

    message = "reading comparison report"
    current_app.logger.audit(message, request=request)
    return comparison_report(
        system_ids=system_ids,
        baseline_ids=baseline_ids,
        historical_sys_profile_ids=historical_sys_profile_ids,
        reference_id=reference_id,
        auth_key=auth_key,
        data_format=data_format,
        short_circuit=short_circuit,
    )


@section.before_app_request
def log_username():
    message = "logging username"
    current_app.logger.audit(message, request=request)
    view_helpers.log_username(current_app.logger, request)


@section.before_app_request
def ensure_entitled():
    message = "Ensuring entitlement"
    current_app.logger.audit(message, request=request)
    return view_helpers.ensure_entitled(request, app_config.get_app_name(), current_app.logger)


@section.before_app_request
def ensure_rbac_comparisons_read():
    # permissions consist of a list of "or" permissions where any will work,
    # and each sublist is a set of "and" permissions that all must be true.
    # For example:
    # permissions=[["drift:*:*"], ["drift:notifications:read", "drift:baselines:read"]]
    # If we just have *:*, it works, but if not, we need both notifications:read and
    # baselines:read in order to allow access.
    message = "Ensuring RBAC permission"
    current_app.logger.audit(message, request=request)
    return view_helpers.ensure_has_permission(
        permissions=[["drift:*:*"], ["drift:comparisons:read"]],
        application="drift",
        app_name="drift",
        request=request,
        logger=current_app.logger,
        request_metric=metrics.rbac_requests,
        exception_metric=metrics.rbac_exceptions,
    )


@section.before_app_request
def ensure_account_number():
    message = "Validating account number"
    current_app.logger.audit(message, request=request)
    return view_helpers.ensure_account_number(request, current_app.logger)
