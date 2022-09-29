from http import HTTPStatus

import jsonpatch
import jsonpointer

from flask import Blueprint, current_app, request
from kerlescan import profile_parser, view_helpers
from kerlescan.exceptions import HTTPError, ItemNotReturned, RBACDenied
from kerlescan.hsp_service_interface import fetch_historical_sys_profiles
from kerlescan.inventory_service_interface import fetch_systems_with_profiles
from kerlescan.paginate import build_paginated_baseline_list_response
from kerlescan.service_interface import get_key_from_headers
from kerlescan.view_helpers import validate_uuids
from sqlalchemy import func
from sqlalchemy.orm.session import make_transient

from system_baseline import metrics, validators
from system_baseline.exceptions import FactValidationError
from system_baseline.global_helpers import (
    ensure_rbac_baselines_read,
    ensure_rbac_baselines_write,
    ensure_rbac_inventory_read,
    ensure_rbac_notifications_read,
    ensure_rbac_notifications_write,
)
from system_baseline.models import SystemBaseline, SystemBaselineMappedSystem, db
from system_baseline.version import app_version


section = Blueprint("v1", __name__)

FACTS_MAXSIZE = 2 ** 19  # 512KB


def _get_total_available_baselines():
    """
    return a count of total number of baselines available for an account
    """
    account_number = view_helpers.get_account_number(request)
    org_id = view_helpers.get_org_id(request)

    if org_id:
        query = SystemBaseline.query.filter(SystemBaseline.org_id == org_id)
    else:
        query = SystemBaseline.query.filter(SystemBaseline.account == account_number)

    result = query.count()

    message = "counted baselines"
    current_app.logger.audit(message, request=request, success=True)

    return result


def get_version():
    """
    return the service version
    """
    return {"version": app_version}


@metrics.baseline_fetch_requests.time()
@metrics.api_exceptions.count_exceptions()
def get_baselines_by_ids(baseline_ids, limit, offset, order_by, order_how):
    """
    return a list of baselines given their ID
    """
    ensure_rbac_baselines_read()
    validate_uuids(baseline_ids)
    if len(set(baseline_ids)) < len(baseline_ids):
        message = "duplicate IDs in request"
        current_app.logger.audit(message, request=request, success=False)
        raise HTTPError(HTTPStatus.BAD_REQUEST, message=message)

    account_number = view_helpers.get_account_number(request)
    org_id = view_helpers.get_org_id(request)

    if org_id:
        query = SystemBaseline.query.filter(
            SystemBaseline.org_id == org_id, SystemBaseline.id.in_(baseline_ids)
        )
    else:
        query = SystemBaseline.query.filter(
            SystemBaseline.account == account_number, SystemBaseline.id.in_(baseline_ids)
        )

    full_results = query.all()

    message = "read baselines"
    current_app.logger.audit(message, request=request)

    if len(full_results) < len(baseline_ids):
        fetched_ids = {str(result.id) for result in full_results}
        missing_ids = set(baseline_ids) - fetched_ids

        message = "ids [%s] not available to display" % ", ".join(missing_ids)
        current_app.logger.audit(message, request=request, success=False)
        raise HTTPError(
            HTTPStatus.NOT_FOUND,
            message=message,
        )

    count = query.count()

    message = "counted baselines"
    current_app.logger.audit(message, request=request)

    total_available = _get_total_available_baselines()

    query = _create_ordering(order_by, order_how, query)
    query = query.limit(limit).offset(offset)

    query_results = query.all()

    message = "read baselines"
    current_app.logger.audit(message, request=request)

    json_list = [baseline.to_json(withhold_facts=False) for baseline in query_results]

    """
    mapped_systems_count is a list of baseline ids and their associated systems counts.
    for loop adds mapped system count for each baseline in the list and sets to 0 if none
    """
    mapped_systems_count = SystemBaselineMappedSystem.get_mapped_system_count(
        account_number, org_id
    )
    for baseline in json_list:
        baseline["mapped_system_count"] = 0
        for baseline_count in mapped_systems_count:
            if baseline["id"] == str(baseline_count[0]):
                baseline["mapped_system_count"] = baseline_count[1]
    return build_paginated_baseline_list_response(
        limit, offset, order_by, order_how, json_list, total_available, count
    )


@metrics.baseline_delete_requests.time()
@metrics.api_exceptions.count_exceptions()
def delete_baselines_by_ids(baseline_ids):
    """
    delete a list of baselines given their ID
    """
    ensure_rbac_baselines_write()
    validate_uuids(baseline_ids)
    if len(set(baseline_ids)) < len(baseline_ids):
        message = "duplicate IDs in request"
        current_app.logger.audit(message, request=request, success=False)
        raise HTTPError(HTTPStatus.BAD_REQUEST, message=message)

    _delete_baselines(baseline_ids)

    message = "deleted baselines"
    current_app.logger.audit(message, request=request, success=True)
    return "OK"


@metrics.baseline_delete_requests.time()
@metrics.api_exceptions.count_exceptions()
def create_deletion_request(body):
    """
    delete a list of baselines given their IDs as a list
    """
    ensure_rbac_baselines_write()
    baseline_ids = body["baseline_ids"]
    validate_uuids(baseline_ids)

    _delete_baselines(baseline_ids)

    message = "deleted baselines"
    current_app.logger.audit(message, request=request, success=True)
    return "OK"


def _delete_baselines(baseline_ids):
    """
    delete baselines
    """
    account_number = view_helpers.get_account_number(request)
    org_id = view_helpers.get_org_id(request)
    if org_id:
        query = SystemBaseline.query.filter(
            SystemBaseline.org_id == org_id, SystemBaseline.id.in_(baseline_ids)
        )
    else:
        query = SystemBaseline.query.filter(
            SystemBaseline.account == account_number, SystemBaseline.id.in_(baseline_ids)
        )

    full_results = query.all()

    message = "read baselines"
    current_app.logger.audit(message, request=request)

    if len(full_results) < len(baseline_ids):
        fetched_ids = {str(result.id) for result in full_results}
        missing_ids = set(baseline_ids) - fetched_ids

        message = "ids [%s] not available to delete" % ", ".join(missing_ids)
        current_app.logger.audit(message, request=request, success=False)
        raise HTTPError(
            HTTPStatus.NOT_FOUND,
            message=message,
        )

    for system_baseline in full_results:
        db.session.delete(system_baseline)

    db.session.commit()

    message = "deleted baselines"
    current_app.logger.audit(message, request=request)


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
    elif order_by == "updated":
        if order_how == "DESC":
            query = query.order_by(SystemBaseline.modified_on.desc())
        elif order_how == "ASC":
            query = query.order_by(SystemBaseline.modified_on.asc())

    return query


@metrics.baseline_fetch_all_requests.time()
@metrics.api_exceptions.count_exceptions()
def get_baselines(limit, offset, order_by, order_how, display_name=None):
    """
    return a list of baselines given their display_name
    if no display_names given, return a list of all baselines for this account
    """
    ensure_rbac_baselines_read()
    account_number = view_helpers.get_account_number(request)
    org_id = view_helpers.get_org_id(request)
    if org_id:
        query = SystemBaseline.query.filter(SystemBaseline.org_id == org_id)
    else:
        query = SystemBaseline.query.filter(SystemBaseline.account == account_number)

    link_args_dict = {}
    if display_name:
        link_args_dict["display_name"] = display_name
        query = query.filter(
            func.lower(SystemBaseline.display_name).contains(display_name.lower(), autoescape=True)
        )

    count = query.count()

    message = "counted baselines"
    current_app.logger.audit(message, request=request)

    total_available = _get_total_available_baselines()

    message = "counted total available baselines"
    current_app.logger.audit(message, request=request)

    query = _create_ordering(order_by, order_how, query)

    query = query.limit(limit).offset(offset)

    query_results = query.all()

    message = "read baselines"
    current_app.logger.audit(message, request=request)

    json_list = [baseline.to_json(withhold_facts=True) for baseline in query_results]

    # DRFT-830
    # temporarily check
    # is systems are being present in inventory
    check_dirty_baselines(query_results)

    """
    mapped_systems_count is a list of baseline ids and their associated systems counts.
    for loop adds mapped system count for each baseline in the list and sets to 0 if none
    """
    mapped_systems_count = SystemBaselineMappedSystem.get_mapped_system_count(
        account_number, org_id
    )
    for baseline in json_list:
        baseline["mapped_system_count"] = 0
        for baseline_count in mapped_systems_count:
            if baseline["id"] == str(baseline_count[0]):
                baseline["mapped_system_count"] = baseline_count[1]

    return build_paginated_baseline_list_response(
        limit,
        offset,
        order_by,
        order_how,
        json_list,
        total_available,
        count,
        args_dict=link_args_dict,
    )


def check_dirty_baselines(baselines):
    auth_key = get_key_from_headers(request.headers)
    account_number = view_helpers.get_account_number(request)
    org_id = view_helpers.get_org_id(request)
    for baseline in baselines:
        if baseline.dirty_systems:
            for system_id in baseline.mapped_system_ids():
                try:
                    # fetch system from inventory
                    message = "read system with profiles"
                    current_app.logger.audit(message, request=request)
                    fetch_systems_with_profiles(
                        [system_id], auth_key, current_app.logger, get_event_counters()
                    )
                except ItemNotReturned:
                    # not in inventory => delete in our db
                    try:
                        SystemBaselineMappedSystem.delete_by_system_ids(
                            [system_id], account_number, org_id
                        )
                    except ValueError as error:
                        message = str(error)
                        current_app.logger.audit(message, request=request, success=False)
                    except Exception:
                        message = "Unknown error when deleting system with baseline"
                        current_app.logger.audit(message, request=request, success=False)

            baseline.dirty_systems = False
            db.session.add(baseline)

    db.session.commit()


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
        "systems_compared_no_sysprofile": metrics.inventory_service_no_profile,
        "inventory_service_requests": metrics.inventory_service_requests,
        "inventory_service_exceptions": metrics.inventory_service_exceptions,
        "hsp_service_requests": metrics.hsp_service_requests,
        "hsp_service_exceptions": metrics.hsp_service_exceptions,
    }


@metrics.baseline_create_requests.time()
@metrics.api_exceptions.count_exceptions()
def create_baseline(system_baseline_in):
    """
    create a baseline
    """
    ensure_rbac_baselines_write()
    account_number = view_helpers.get_account_number(request)
    org_id = view_helpers.get_org_id(request)

    if "values" in system_baseline_in and "value" in system_baseline_in:
        message = "'values' and 'value' cannot both be defined for system baseline"
        current_app.logger.audit(message, request=request, success=False)
        raise HTTPError(
            HTTPStatus.BAD_REQUEST,
            message=message,
        )

    _check_for_existing_display_name(system_baseline_in["display_name"], account_number, org_id)
    _check_for_whitespace_in_display_name(system_baseline_in["display_name"])

    message = "counted baselines"
    current_app.logger.audit(message, request=request)

    baseline_facts = []
    if "baseline_facts" in system_baseline_in:
        if "inventory_uuid" in system_baseline_in:
            message = "Both baseline facts and inventory id provided, can clone only one."
            current_app.logger.audit(message, request=request, success=False)
            raise HTTPError(
                HTTPStatus.BAD_REQUEST,
                message=message,
            )
        if "hsp_uuid" in system_baseline_in:
            message = "Both baseline facts and hsp id provided, can clone only one."
            current_app.logger.audit(message, request=request, success=False)
            raise HTTPError(
                HTTPStatus.BAD_REQUEST,
                message=message,
            )
        baseline_facts = system_baseline_in["baseline_facts"]
    elif "hsp_uuid" in system_baseline_in:
        if "inventory_uuid" in system_baseline_in:
            message = "Both hsp id and system id provided, can clone only one."
            current_app.logger.audit(message, request=request, success=False)
            raise HTTPError(
                HTTPStatus.BAD_REQUEST,
                message=message,
            )
        validate_uuids([system_baseline_in["hsp_uuid"]])
        auth_key = get_key_from_headers(request.headers)
        try:
            hsp = fetch_historical_sys_profiles(
                [system_baseline_in["hsp_uuid"]],
                auth_key,
                current_app.logger,
                get_event_counters(),
            )[0]
            message = "read historical system profiles"
            current_app.logger.audit(message, request=request)
        except ItemNotReturned:
            message = "hsp UUID %s not available" % system_baseline_in["hsp_uuid"]
            current_app.logger.audit(message, request=request, success=False)
            raise HTTPError(
                HTTPStatus.NOT_FOUND,
                message=message,
            )
        except RBACDenied as error:
            message = error.message
            current_app.logger.audit(message, request=request, success=False)
            raise HTTPError(HTTPStatus.FORBIDDEN, message=message)

        system_name = "clone_from_hsp_unused"
        baseline_facts = _parse_from_sysprofile(
            hsp["system_profile"], system_name, current_app.logger
        )
    elif "inventory_uuid" in system_baseline_in:
        validate_uuids([system_baseline_in["inventory_uuid"]])
        auth_key = get_key_from_headers(request.headers)
        try:
            system_with_profile = fetch_systems_with_profiles(
                [system_baseline_in["inventory_uuid"]],
                auth_key,
                current_app.logger,
                get_event_counters(),
            )[0]
            message = "read system with profiles"
            current_app.logger.audit(message, request=request)
        except ItemNotReturned:
            message = "inventory UUID %s not available" % system_baseline_in["inventory_uuid"]
            current_app.logger.audit(message, request=request, success=False)
            raise HTTPError(
                HTTPStatus.NOT_FOUND,
                message=message,
            )
        except RBACDenied as error:
            message = error.message
            current_app.logger.audit(message, request=request, success=False)
            raise HTTPError(HTTPStatus.FORBIDDEN, message=message)

        system_name = profile_parser.get_name(system_with_profile)
        baseline_facts = _parse_from_sysprofile(
            system_with_profile["system_profile"], system_name, current_app.logger
        )

    try:
        _validate_facts(baseline_facts)
    except FactValidationError as error:
        message = error.message
        current_app.logger.audit(message, request=request, success=False)
        raise HTTPError(HTTPStatus.BAD_REQUEST, message=message)

    baseline = SystemBaseline(
        account=account_number,
        org_id=org_id,
        display_name=system_baseline_in["display_name"],
        baseline_facts=baseline_facts,
    )
    baseline.baseline_facts = _sort_baseline_facts(baseline.baseline_facts)
    db.session.add(baseline)

    db.session.commit()  # commit now so we get a created/updated time before json conversion

    message = "create baselines"
    current_app.logger.audit(message, request=request)

    return baseline.to_json(withhold_systems_count=False)


def _check_for_existing_display_name(display_name, account_number, org_id):
    """
    check to see if a display name already exists for an account, and raise an exception if so.
    """
    if org_id:
        query = SystemBaseline.query.filter(
            SystemBaseline.org_id == org_id,
            SystemBaseline.display_name == display_name,
        )
    else:
        query = SystemBaseline.query.filter(
            SystemBaseline.account == account_number,
            SystemBaseline.display_name == display_name,
        )

    count = query.count()
    message = "counted baselines"
    current_app.logger.audit(message, request=request)

    if count > 0:
        message = "A baseline with this name already exists."
        current_app.logger.audit(message, request=request, success=False)
        raise HTTPError(
            HTTPStatus.BAD_REQUEST,
            message=message,
        )


def _check_for_whitespace_in_display_name(display_name):
    """
    check to see if the display name has leading or trailing whitespace
    """
    if display_name and (not validators.check_whitespace(display_name)):
        message = "Baseline name cannot have leading or trailing whitespace."
        current_app.logger.audit(message, request=request, success=False)
        raise HTTPError(
            HTTPStatus.BAD_REQUEST,
            message=message,
        )


def _sort_baseline_facts(baseline_facts):
    """
    helper method to sort baseline facts by name before saving to the DB.
    """
    sorted_baseline_facts = sorted(baseline_facts, key=lambda fact: fact["name"].lower())
    for fact in sorted_baseline_facts:
        if "values" in fact:
            fact["values"] = sorted(fact["values"], key=lambda fact: fact["name"].lower())
    return sorted_baseline_facts


def _parse_from_sysprofile(system_profile, system_name, logger):
    parsed_profile = profile_parser.parse_profile(system_profile, system_name, current_app.logger)
    facts = []
    for fact in parsed_profile:
        if fact not in ["id", "name"] and parsed_profile[fact] not in [
            "N/A",
            "None",
            None,
        ]:
            facts.append({"name": fact, "value": parsed_profile[fact]})

    return group_baselines(facts)


@metrics.baseline_create_requests.time()
@metrics.api_exceptions.count_exceptions()
def copy_baseline_by_id(baseline_id, display_name):
    """
    create a new baseline given an existing ID
    """
    ensure_rbac_baselines_write()
    validate_uuids([baseline_id])

    # ensure display_name is not null
    if not display_name:
        message = "no value given for display_name"
        current_app.logger.audit(message, request=request, success=False)
        raise HTTPError(HTTPStatus.BAD_REQUEST, message=message)

    account_number = view_helpers.get_account_number(request)
    org_id = view_helpers.get_org_id(request)

    _check_for_existing_display_name(display_name, account_number, org_id)
    _check_for_whitespace_in_display_name(display_name)

    message = "counted baselines"
    current_app.logger.audit(message, request=request)

    if org_id:
        query = SystemBaseline.query.filter(
            SystemBaseline.org_id == org_id, SystemBaseline.id == baseline_id
        )
    else:
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

    message = "created baselines"
    current_app.logger.audit(message, request=request)

    return copy_baseline.to_json(withhold_systems_count=False)


def update_baseline(baseline_id, system_baseline_patch):
    """
    update a baseline
    """
    current_app.logger.error(system_baseline_patch)
    ensure_rbac_baselines_write()
    validate_uuids([baseline_id])

    account_number = view_helpers.get_account_number(request)
    org_id = view_helpers.get_org_id(request)
    _check_for_whitespace_in_display_name(system_baseline_patch["display_name"])

    # this query is a bit different than what's in _check_for_existing_display_name,
    # since it's OK if the display name is used by the baseline we are updating
    if org_id:
        existing_display_name_query = SystemBaseline.query.filter(
            SystemBaseline.org_id == org_id,
            SystemBaseline.id != baseline_id,
            SystemBaseline.display_name == system_baseline_patch["display_name"],
        )
    else:
        existing_display_name_query = SystemBaseline.query.filter(
            SystemBaseline.account == account_number,
            SystemBaseline.id != baseline_id,
            SystemBaseline.display_name == system_baseline_patch["display_name"],
        )

    if existing_display_name_query.count() > 0:
        message = "A baseline with this name already exists."
        current_app.logger.audit(message, request=request, success=False)
        raise HTTPError(
            HTTPStatus.BAD_REQUEST,
            message=message,
        )

    if org_id:
        query = SystemBaseline.query.filter(
            SystemBaseline.org_id == org_id, SystemBaseline.id == baseline_id
        )
    else:
        query = SystemBaseline.query.filter(
            SystemBaseline.account == account_number, SystemBaseline.id == baseline_id
        )

    baseline = query.first_or_404()
    message = "read baselines"
    current_app.logger.audit(message, request=request)

    try:
        updated_facts = jsonpatch.apply_patch(
            baseline.baseline_facts, system_baseline_patch["facts_patch"]
        )
        _validate_facts(updated_facts)
        baseline.baseline_facts = updated_facts
    except FactValidationError as error:
        message = error.message
        current_app.logger.audit(message, request=request, success=False)
        raise HTTPError(HTTPStatus.BAD_REQUEST, message=message)
    except (jsonpatch.JsonPatchException, jsonpointer.JsonPointerException):
        message = "unable to apply patch to baseline"
        current_app.logger.audit(message, request=request, success=False)
        raise HTTPError(HTTPStatus.BAD_REQUEST, message=message)

    baseline.display_name = system_baseline_patch["display_name"]
    if "notifications_enabled" in system_baseline_patch.keys():
        baseline.notifications_enabled = system_baseline_patch["notifications_enabled"]
    baseline.baseline_facts = _sort_baseline_facts(baseline.baseline_facts)
    db.session.add(baseline)

    db.session.commit()

    message = "updated baselines"
    current_app.logger.audit(message, request=request)

    # pull baseline again so we have the correct updated timestamp and fact count
    if org_id:
        query = SystemBaseline.query.filter(
            SystemBaseline.account == account_number, SystemBaseline.id == baseline_id
        )
    else:
        query = SystemBaseline.query.filter(
            SystemBaseline.org_id == org_id, SystemBaseline.id == baseline_id
        )
    return [query.first().to_json()]


def list_systems_with_baseline(baseline_id):
    ensure_rbac_notifications_read()
    ensure_rbac_inventory_read()
    validate_uuids([baseline_id])
    account_number = view_helpers.get_account_number(request)
    org_id = view_helpers.get_org_id(request)

    if org_id:
        query = SystemBaseline.query.filter(
            SystemBaseline.org_id == org_id, SystemBaseline.id == baseline_id
        )
    else:
        query = SystemBaseline.query.filter(
            SystemBaseline.account == account_number, SystemBaseline.id == baseline_id
        )
    baseline = query.first_or_404()

    message = "read baseline"
    current_app.logger.audit(message, request=request, success=True)

    try:
        system_ids = baseline.mapped_system_ids()
    except ValueError as error:
        message = str(error)
        current_app.logger.audit(message, request=request, success=False)
        raise HTTPError(HTTPStatus.BAD_REQUEST, message=message)
    except Exception:
        message = "Unknown error when reading mapped system ids"
        current_app.logger.audit(message, request=request, success=False)
        raise

    return {"system_ids": system_ids}


def create_systems_with_baseline(baseline_id, body):
    ensure_rbac_notifications_write()
    validate_uuids([baseline_id])
    system_ids = body["system_ids"]
    validate_uuids(system_ids)
    if len(set(system_ids)) < len(system_ids):
        message = "duplicate IDs in request"
        current_app.logger.audit(message, request=request, success=False)
        raise HTTPError(HTTPStatus.BAD_REQUEST, message=message)
    account_number = view_helpers.get_account_number(request)
    org_id = view_helpers.get_org_id(request)

    if org_id:
        query = SystemBaseline.query.filter(
            SystemBaseline.org_id == org_id, SystemBaseline.id == baseline_id
        )
    else:
        query = SystemBaseline.query.filter(
            SystemBaseline.account == account_number, SystemBaseline.id == baseline_id
        )
    baseline = query.first_or_404()

    message = "read baseline"
    current_app.logger.audit(message, request=request, success=True)

    try:
        for system_id in system_ids:
            baseline.add_mapped_system(system_id)

        db.session.commit()
    except ValueError as error:
        message = str(error)
        current_app.logger.audit(message, request=request, success=False)
        raise HTTPError(HTTPStatus.BAD_REQUEST, message=message)
    except Exception:
        message = "Unknown error when creating systems with baseline"
        current_app.logger.audit(message, request=request, success=False)
        raise

    message = "created systems with baseline"
    current_app.logger.audit(message, request=request, success=True)

    system_ids = baseline.mapped_system_ids()
    return {"system_ids": system_ids}


def delete_systems_with_baseline(baseline_id, system_ids):
    ensure_rbac_notifications_write()
    validate_uuids([baseline_id])
    validate_uuids(system_ids)
    if len(set(system_ids)) < len(system_ids):
        message = "duplicate IDs in request"
        current_app.logger.audit(message, request=request, success=False)
        raise HTTPError(HTTPStatus.BAD_REQUEST, message=message)
    account_number = view_helpers.get_account_number(request)
    org_id = view_helpers.get_org_id(request)

    if org_id:
        query = SystemBaseline.query.filter(
            SystemBaseline.org_id == org_id, SystemBaseline.id == baseline_id
        )
    else:
        query = SystemBaseline.query.filter(
            SystemBaseline.account == account_number, SystemBaseline.id == baseline_id
        )
    baseline = query.first_or_404()

    message = "read baseline"
    current_app.logger.audit(message, request=request, success=True)

    try:
        for system_id in system_ids:
            baseline.remove_mapped_system(system_id)
        db.session.commit()
    except ValueError as error:
        message = str(error)
        current_app.logger.audit(message, request=request, success=False)
        raise HTTPError(HTTPStatus.BAD_REQUEST, message=message)
    except Exception:
        message = "Unknown error when deleting systems with baseline"
        current_app.logger.audit(message, request=request, success=False)
        raise

    message = "deleted systems with baseline"
    current_app.logger.audit(message, request=request, success=True)

    system_ids = baseline.mapped_system_ids()
    return "OK"


def create_deletion_request_for_systems(baseline_id, body):
    ensure_rbac_notifications_write()
    validate_uuids([baseline_id])
    system_ids = body["system_ids"]
    validate_uuids(system_ids)

    delete_systems_with_baseline(baseline_id, system_ids)
    return "OK"


def _validate_facts(facts):
    """
    helper to run common validations
    """
    validators.check_facts_length(facts)
    validators.check_for_duplicate_names(facts)
    validators.check_for_empty_name_values(facts)
    validators.check_for_invalid_whitespace_name_values(facts)
    validators.check_for_value_values(facts)
    validators.check_name_value_length(facts)
