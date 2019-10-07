from flask import Blueprint, request, current_app, Response
from http import HTTPStatus
import json
import jsonpatch
import jsonpointer

from sqlalchemy.orm.session import make_transient

from kerlescan import view_helpers
from kerlescan import profile_parser
from kerlescan.exceptions import HTTPError
from kerlescan.inventory_service_interface import fetch_systems_with_profiles
from kerlescan.service_interface import get_key_from_headers

from system_baseline import metrics, app_config, validators
from system_baseline.models import SystemBaseline, db
from system_baseline.exceptions import FactValidationError

section = Blueprint("v0", __name__)

pagination_link_template = "%s?limit=%s&offset=%s&order_by=%s&order_how=%s"

FACTS_MAXSIZE = 2 ** 19  # 512KB


def _create_first_link(path, limit, offset, total, order_by, order_how):
    first_link = pagination_link_template % (path, limit, 0, order_by, order_how)
    return first_link


def _create_previous_link(path, limit, offset, total, order_by, order_how):
    # if we are at the beginning, do not create a previous link
    if offset == 0 or offset - limit < 0:
        return _create_first_link(path, limit, offset, total, order_by, order_how)
    previous_link = pagination_link_template % (
        request.path,
        limit,
        offset - limit,
        order_by,
        order_how,
    )
    return previous_link


def _create_next_link(path, limit, offset, total, order_by, order_how):
    # if we are at the end, do not create a next link
    if limit + offset >= total:
        return _create_last_link(path, limit, offset, total, order_by, order_how)
    next_link = pagination_link_template % (
        request.path,
        limit,
        limit + offset,
        order_by,
        order_how,
    )
    return next_link


def _create_last_link(path, limit, offset, total, order_by, order_how):
    final_offset = total - limit if (total - limit) >= 0 else 0
    last_link = pagination_link_template % (
        path,
        limit,
        final_offset,
        order_by,
        order_how,
    )
    return last_link


def _build_paginated_baseline_list_response(
    total, limit, offset, order_by, order_how, baseline_list, withhold_facts=False
):
    json_baseline_list = [
        baseline.to_json(withhold_facts=withhold_facts) for baseline in baseline_list
    ]
    link_params = {
        "path": request.path,
        "limit": limit,
        "offset": offset,
        "order_by": order_by,
        "order_how": order_how,
        "total": total,
    }
    json_output = {
        "meta": {"count": total, "total_available": _get_total_baseline_count()},
        "links": {
            "first": _create_first_link(**link_params),
            "next": _create_next_link(**link_params),
            "previous": _create_previous_link(**link_params),
            "last": _create_last_link(**link_params),
        },
        "data": json_baseline_list,
    }

    return _build_json_response(json_output)


def _build_json_response(json_data, status=200):
    return Response(json.dumps(json_data), status=status, mimetype="application/json")


def _get_total_baseline_count():
    """
    return a count of total number of baselines available for an account
    """
    account_number = view_helpers.get_account_number(request)
    query = SystemBaseline.query.filter(SystemBaseline.account == account_number)
    return query.count()


@metrics.baseline_fetch_requests.time()
@metrics.api_exceptions.count_exceptions()
def get_baselines_by_ids(baseline_ids, limit, order_by, order_how, offset):
    """
    return a list of baselines given their ID
    """
    _validate_uuids(baseline_ids)
    account_number = view_helpers.get_account_number(request)
    query = SystemBaseline.query.filter(
        SystemBaseline.account == account_number, SystemBaseline.id.in_(baseline_ids)
    )
    total_count = query.count()

    query = _create_ordering(order_by, order_how, query)
    query = query.limit(limit).offset(offset)
    query_results = query.all()

    return _build_paginated_baseline_list_response(
        total_count,
        limit,
        offset,
        order_by,
        order_how,
        query_results,
        withhold_facts=False,
    )


@metrics.baseline_delete_requests.time()
@metrics.api_exceptions.count_exceptions()
def delete_baselines_by_ids(baseline_ids):
    """
    delete a list of baselines given their ID
    """
    _validate_uuids(baseline_ids)
    account_number = view_helpers.get_account_number(request)
    query = SystemBaseline.query.filter(
        SystemBaseline.account == account_number, SystemBaseline.id.in_(baseline_ids)
    )
    query.delete(synchronize_session="fetch")
    db.session.commit()
    return "OK"


def _create_ordering(order_by, order_how, query):
    """
    helper method to set ordering on query. `order_by` and `order_how` are
    guaranteed to be populated as "DESC" or "ASC" via the openapi definition.
    """
    if order_by == "display_name":
        if order_how == "DESC":
            query = query.order_by(SystemBaseline.display_name.desc())
        elif order_how == "ASC":
            query = query.order_by(SystemBaseline.display_name.asc())
    elif order_by == "created_on":
        if order_how == "DESC":
            query = query.order_by(SystemBaseline.created_on.desc())
        elif order_how == "ASC":
            query = query.order_by(SystemBaseline.created_on.asc())

    return query


@metrics.baseline_fetch_all_requests.time()
@metrics.api_exceptions.count_exceptions()
def get_baselines(limit, offset, order_by, order_how, display_name=None):
    """
    return a list of baselines given their ID
    """
    account_number = view_helpers.get_account_number(request)
    query = SystemBaseline.query.filter(SystemBaseline.account == account_number)

    if display_name:
        query = query.filter(SystemBaseline.display_name.contains(display_name))

    total_count = query.count()

    query = _create_ordering(order_by, order_how, query)

    query = query.limit(limit).offset(offset)
    query_results = query.all()

    return _build_paginated_baseline_list_response(
        total_count,
        limit,
        offset,
        order_by,
        order_how,
        query_results,
        withhold_facts=True,
    )


def group_baselines(baseline):
    """
    return a grouped baseline
    """

    def _get_group_name(name):
        n, _, _ = name.partition(".")
        return n

    def _get_value_name(name):
        _, _, n = name.partition(".")
        return n

    def _find_group(name):
        for group in grouped_baseline:
            if group["name"] == name:
                return group

    # build out group names
    group_names = {_get_group_name(b["name"]) for b in baseline if "." in b["name"]}
    grouped_baseline = []
    for group_name in group_names:
        grouped_baseline.append({"name": group_name, "values": []})

    # populate groups
    for fact in baseline:
        if "." in fact["name"]:
            group = _find_group(_get_group_name(fact["name"]))
            fact["name"] = _get_value_name(fact["name"])
            group["values"].append(fact)
        else:
            grouped_baseline.append(fact)

    return grouped_baseline


def get_event_counters():
    """
    small helper to create a dict of event counters
    """
    return {
        "systems_compared_no_sysprofile": metrics.systems_compared_no_sysprofile,
        "inventory_service_requests": metrics.inventory_service_requests,
        "inventory_service_exceptions": metrics.inventory_service_exceptions,
    }


@metrics.baseline_create_requests.time()
@metrics.api_exceptions.count_exceptions()
def create_baseline(system_baseline_in):
    """
    create a baseline
    """
    account_number = view_helpers.get_account_number(request)

    if "values" in system_baseline_in and "value" in system_baseline_in:
        raise HTTPError(
            HTTPStatus.BAD_REQUEST,
            message="'values' and 'value' cannot both be defined for system baseline",
        )

    query = SystemBaseline.query.filter(
        SystemBaseline.account == account_number,
        SystemBaseline.display_name == system_baseline_in["display_name"],
    )

    if query.count() > 0:
        raise HTTPError(
            HTTPStatus.BAD_REQUEST,
            message="display_name '%s' already used for this account"
            % system_baseline_in["display_name"],
        )

    baseline_facts = []
    if "baseline_facts" in system_baseline_in:
        baseline_facts = system_baseline_in["baseline_facts"]
    elif "inventory_uuid" in system_baseline_in:
        auth_key = get_key_from_headers(request.headers)
        system_with_profile = fetch_systems_with_profiles(
            [system_baseline_in["inventory_uuid"]],
            auth_key,
            current_app.logger,
            get_event_counters(),
        )[0]

        system_name = profile_parser.get_name(system_with_profile)
        parsed_profile = profile_parser.parse_profile(
            system_with_profile["system_profile"], system_name, current_app.logger
        )
        facts = []
        for fact in parsed_profile:
            if fact not in ["id", "name"] and parsed_profile[fact] not in [
                "N/A",
                "None",
                None,
            ]:
                facts.append({"name": fact, "value": parsed_profile[fact]})

        baseline_facts = group_baselines(facts)

    try:
        validators.check_facts_length(baseline_facts)
        validators.check_for_duplicate_names(baseline_facts)
    except FactValidationError as e:
        raise HTTPError(HTTPStatus.BAD_REQUEST, message=e.message)

    baseline = SystemBaseline(
        account=account_number,
        display_name=system_baseline_in["display_name"],
        baseline_facts=baseline_facts,
    )
    db.session.add(baseline)
    db.session.commit()  # commit now so we get a created/updated time before json conversion

    return baseline.to_json()


def _validate_uuids(uuids):
    """
    helper method to raise user-friendly exception on UUID format errors
    """
    try:
        validators.check_uuids(uuids)
    except ValueError:
        raise HTTPError(
            HTTPStatus.BAD_REQUEST,
            message="malformed UUID requested (%s)" % ",".join(uuids),
        )


@metrics.baseline_create_requests.time()
@metrics.api_exceptions.count_exceptions()
def copy_baseline_by_id(baseline_id, display_name):
    """
    create a new baseline given an existing ID
    """
    _validate_uuids([baseline_id])

    account_number = view_helpers.get_account_number(request)
    query = SystemBaseline.query.filter(
        SystemBaseline.account == account_number, SystemBaseline.id == baseline_id
    )

    copy_baseline = query.first_or_404()
    db.session.expunge(copy_baseline)
    make_transient(copy_baseline)
    copy_baseline.id = None
    copy_baseline.created_on = None
    copy_baseline.modified_on = None
    copy_baseline.display_name = display_name
    db.session.add(copy_baseline)
    db.session.commit()
    return copy_baseline.to_json()


def update_baseline(baseline_id, system_baseline_patch):
    """
    update a baseline
    """
    _validate_uuids([baseline_id])

    account_number = view_helpers.get_account_number(request)

    existing_display_name_query = SystemBaseline.query.filter(
        SystemBaseline.account == account_number,
        SystemBaseline.id != baseline_id,
        SystemBaseline.display_name == system_baseline_patch["display_name"],
    )

    if existing_display_name_query.count() > 0:
        raise HTTPError(
            HTTPStatus.BAD_REQUEST,
            message="display_name '%s' already used for this account"
            % system_baseline_patch["display_name"],
        )

    query = SystemBaseline.query.filter(
        SystemBaseline.account == account_number, SystemBaseline.id == baseline_id
    )
    baseline = query.first_or_404()

    try:
        updated_facts = jsonpatch.apply_patch(
            baseline.baseline_facts, system_baseline_patch["facts_patch"]
        )
        validators.check_facts_length(updated_facts)
        baseline.baseline_facts = updated_facts
    except (jsonpatch.JsonPatchException, jsonpointer.JsonPointerException):
        raise HTTPError(
            HTTPStatus.BAD_REQUEST, message="unable to apply patch to baseline"
        )

    baseline.display_name = system_baseline_patch["display_name"]

    db.session.add(baseline)
    db.session.commit()

    # pull baseline again so we have the correct updated timestamp and fact count
    query = SystemBaseline.query.filter(
        SystemBaseline.account == account_number, SystemBaseline.id == baseline_id
    )
    return [query.first().to_json()]


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
