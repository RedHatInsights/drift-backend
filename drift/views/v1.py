import csv
import io

from flask import Blueprint, jsonify, request, current_app, make_response
from http import HTTPStatus
from uuid import UUID

from drift import info_parser, metrics, app_config
from drift.version import app_version
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


def get_version():
    """
    return the service version
    """
    return {"version": app_version}


def get_event_counters():
    """
    small helper to create a dict of event counters
    """
    return {
        "systems_compared_no_sysprofile": metrics.systems_compared_no_sysprofile,
        "inventory_service_requests": metrics.inventory_service_requests,
        "inventory_service_exceptions": metrics.inventory_service_exceptions,
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
    # add baselines to the CSV dict, then systems
    for baseline in comparisons["baselines"]:
        record_ids.append(baseline["id"])
        system_names[baseline["id"]] = baseline["display_name"]

    for system in comparisons["systems"]:
        record_ids.append(system["id"])
        system_names[system["id"]] = system["display_name"]

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
    output.close()
    return result


def comparison_report(system_ids, baseline_ids, auth_key, data_format):
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
        if data_format == "csv":
            output = make_response(_csvify(comparisons))
            output.headers["Content-Disposition"] = "attachment; filename=export.csv"
            output.headers["Content-type"] = "text/csv"
            return output
        else:
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

    data_format = "json"
    if "text/csv" in request.headers.get("accept", []):
        data_format = "csv"

    return comparison_report(system_ids, baseline_ids, auth_key, data_format)


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

    data_format = "json"
    if "text/csv" in request.headers["accept"]:
        data_format = "csv"

    return comparison_report(system_ids, baseline_ids, auth_key, data_format)


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
