from flask import Blueprint, request, current_app, Response
from http import HTTPStatus
import json
from uuid import UUID

from sqlalchemy.orm.session import make_transient

from kerlescan import view_helpers
from kerlescan import profile_parser
from kerlescan.exceptions import HTTPError
from kerlescan.inventory_service_interface import fetch_systems_with_profiles
from kerlescan.service_interface import get_key_from_headers

from system_baseline import metrics, app_config
from system_baseline.models import SystemBaseline, db

section = Blueprint("v0", __name__)

pagination_link_template = "%s?limit=%s&offset=%s"


def _create_first_link(path, limit, offset, total):
    first_link = pagination_link_template % (path, limit, 0)
    return first_link


def _create_previous_link(path, limit, offset, total):
    # if we are at the beginning, do not create a previous link
    if offset == 0 or offset - limit < 0:
        return _create_first_link(path, limit, offset, total)
    previous_link = pagination_link_template % (request.path, limit, offset - limit)
    return previous_link


def _create_next_link(path, limit, offset, total):
    # if we are at the end, do not create a next link
    if limit + offset >= total:
        return _create_last_link(path, limit, offset, total)
    next_link = pagination_link_template % (request.path, limit, limit + offset)
    return next_link


def _create_last_link(path, limit, offset, total):
    final_offset = total - limit if (total - limit) >= 0 else 0
    last_link = pagination_link_template % (path, limit, final_offset)
    return last_link


def _build_paginated_baseline_list_response(
    total, limit, offset, baseline_list, withhold_facts=False
):
    json_baseline_list = [
        baseline.to_json(withhold_facts=withhold_facts) for baseline in baseline_list
    ]
    link_params = {
        "path": request.path,
        "limit": limit,
        "offset": offset,
        "total": total,
    }
    json_output = {
        "meta": {"count": total},
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


def _validate_uuids(baseline_ids):
    """
    helper method to test if a UUID is properly formatted. Will raise an
    exception if format is wrong.
    """
    for baseline_id in baseline_ids:
        try:
            UUID(baseline_id)
        except ValueError:
            raise HTTPError(
                HTTPStatus.BAD_REQUEST,
                message="baseline_id %s is not a UUID" % baseline_id,
            )


@metrics.baseline_fetch_requests.time()
@metrics.api_exceptions.count_exceptions()
def get_baselines_by_ids(baseline_ids, limit, offset):
    """
    return a list of baselines given their ID
    """
    _validate_uuids(baseline_ids)
    account_number = view_helpers.get_account_number(request)
    query = SystemBaseline.query.filter(
        SystemBaseline.account == account_number, SystemBaseline.id.in_(baseline_ids)
    )
    total_count = query.count()

    query = query.order_by(SystemBaseline.created_on, SystemBaseline.id)
    query = query.limit(limit).offset(offset)
    query_results = query.all()

    return _build_paginated_baseline_list_response(
        total_count, limit, offset, query_results, withhold_facts=False
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


@metrics.baseline_fetch_all_requests.time()
@metrics.api_exceptions.count_exceptions()
def get_baselines(limit, offset):
    """
    return a list of baselines given their ID
    """
    account_number = view_helpers.get_account_number(request)
    query = SystemBaseline.query.filter(SystemBaseline.account == account_number)

    total_count = query.count()

    query = query.order_by(SystemBaseline.created_on, SystemBaseline.id)
    query = query.limit(limit).offset(offset)
    query_results = query.all()

    return _build_paginated_baseline_list_response(
        total_count, limit, offset, query_results, withhold_facts=True
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

    baseline = SystemBaseline(
        account=account_number,
        display_name=system_baseline_in["display_name"],
        baseline_facts=baseline_facts,
    )
    db.session.add(baseline)
    db.session.commit()  # commit now so we get a created/updated time before json conversion

    return baseline.to_json()


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
    copy_baseline.display_name = display_name
    db.session.add(copy_baseline)
    db.session.commit()
    return copy_baseline.to_json()


def _merge_baselines(baseline, baseline_updates):
    """
    update a baseline with a partial update set.
    """
    # remove existing baseline facts with the same names
    updated_fact_names = set()
    for update in baseline_updates["baseline_facts"]:
        updated_fact_names.add(update["name"])

    existing_baseline_facts = []
    for existing_fact in baseline.baseline_facts:
        if existing_fact["name"] not in updated_fact_names:
            existing_baseline_facts.append(existing_fact)

    # merge remaining facts with new facts
    baseline.baseline_facts = (
        existing_baseline_facts + baseline_updates["baseline_facts"]
    )
    return baseline


def update_baseline(baseline_id, system_baseline_partial):
    """
    update a baseline
    """
    _validate_uuids([baseline_id])

    account_number = view_helpers.get_account_number(request)
    # check if we are going to conflict with an existing record's name
    if "display_name" in system_baseline_partial:
        display_name_query = SystemBaseline.query.filter(
            SystemBaseline.account == account_number,
            SystemBaseline.display_name == system_baseline_partial["display_name"],
        )
        existing_display_name = display_name_query.first()
        if existing_display_name and existing_display_name.id is not baseline_id:
            raise HTTPError(
                HTTPStatus.BAD_REQUEST,
                message="display_name %s is in use by another record"
                % system_baseline_partial["display_name"],
            )

    query = SystemBaseline.query.filter(
        SystemBaseline.account == account_number, SystemBaseline.id == baseline_id
    )
    existing_baseline = query.first_or_404()
    new_baseline = existing_baseline
    if "baseline_facts" in system_baseline_partial:
        new_baseline = _merge_baselines(existing_baseline, system_baseline_partial)
    if "display_name" in system_baseline_partial:
        new_baseline.display_name = system_baseline_partial["display_name"]
    db.session.add(new_baseline)
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
