import datetime

from collections import Counter
from http import HTTPStatus

from dateutil.relativedelta import relativedelta
from flask import Blueprint, current_app, request
from kerlescan import view_helpers
from kerlescan.exceptions import HTTPError, RBACDenied
from kerlescan.inventory_service_interface import fetch_systems_with_profiles
from kerlescan.service_interface import get_key_from_headers
from kerlescan.view_helpers import validate_uuids

from historical_system_profiles import config, db_interface, metrics


section = Blueprint("v1", __name__)


def get_version():
    """
    return the service version
    """
    return {"version": "1.0.0"}


def _get_current_names_for_profiles(hsps):
    # make a unique list of inventory IDs
    inventory_ids = list({str(h.inventory_id) for h in hsps})

    auth_key = get_key_from_headers(request.headers)

    try:
        systems = fetch_systems_with_profiles(
            inventory_ids,
            auth_key,
            current_app.logger,
            _get_event_counters(),
        )
        message = "read systems"
        current_app.logger.audit(message, request=request, success=True)
    except RBACDenied as error:
        message = error.message
        current_app.logger.audit(message, request=request, success=False)
        raise HTTPError(HTTPStatus.FORBIDDEN, message=message)

    display_names = {system["id"]: system["display_name"] for system in systems}
    enriched_hsps = []
    for hsp in hsps:
        current_display_name = display_names[str(hsp.inventory_id)]
        hsp.system_profile["display_name"] = current_display_name
        enriched_hsps.append(hsp)

    return enriched_hsps


def _filter_old_hsps(hsps):
    """
    removes any HSPs with a captured_date older than now minus the valid profile age

    This compares "apples to apples"; the captured_date is always in UTC, and
    we pull the current time in UTC.
    """
    now = datetime.datetime.now(datetime.timezone.utc)
    cutoff = now - relativedelta(days=config.valid_profile_age_days)

    valid_hsps = []
    for hsp in hsps:
        if hsp.captured_date > cutoff:
            valid_hsps.append(hsp)

    return valid_hsps


def _check_for_missing_ids(requested_ids, result):
    """
    checks a list of returned items against a list of requested IDs, and raises
    an exception if they were not all in the list. requested_ids is a list of
    items, and each item must be an object with an "id" attribute (NOT a dict
    with an "id" key).

    This method does not return anything.
    """
    if len(result) < len(requested_ids):
        returned_ids = {str(item.id) for item in result}
        missing_ids = set(requested_ids) - returned_ids

        message = "ids [%s] not available to display" % ", ".join(missing_ids)
        current_app.logger.audit(message, request=request, success=False)
        raise HTTPError(
            HTTPStatus.NOT_FOUND,
            message=message,
        )


def _check_for_duplicates(requested_ids):
    """
    raise an exception if there are duplicate strings in the list.

    This method does not return anything.
    """
    duplicate_ids = []
    for item, count in Counter(requested_ids).items():
        if count > 1:
            duplicate_ids.append(item)

    if duplicate_ids:
        message = "duplicate IDs requested: %s" % duplicate_ids
        current_app.logger.audit(message, request=request, success=False)
        raise HTTPError(
            HTTPStatus.BAD_REQUEST,
            message=message,
        )


def get_hsps_by_ids(profile_ids):
    """
    return a list of historical system profiles for the given profile IDs
    """
    validate_uuids(profile_ids)
    _check_for_duplicates(profile_ids)

    account_number = view_helpers.get_account_number(request)

    message = "read historical system profiles"
    current_app.logger.audit(message, request=request)

    result = db_interface.get_hsps_by_profile_ids(profile_ids, account_number)

    # TODO: rely on captured_date and filter in SQL above
    filtered_result = _filter_old_hsps(result)

    _check_for_missing_ids(profile_ids, filtered_result)

    result_with_updated_names = _get_current_names_for_profiles(filtered_result)

    return {"data": [r.to_json() for r in result_with_updated_names]}


def get_hsps_by_inventory_id(inventory_id, limit, offset):
    """
    return a list of historical system profiles for a given inventory id
    """
    validate_uuids([inventory_id])
    account_number = view_helpers.get_account_number(request)

    message = "read historical system profiles"
    current_app.logger.audit(message, request=request)

    query_results = db_interface.get_hsps_by_inventory_id(
        inventory_id, account_number, limit, offset
    )
    valid_profiles = _filter_old_hsps(query_results)

    if not valid_profiles:
        message = "no historical profiles found for inventory_id %s" % inventory_id
        current_app.logger.audit(message, request=request, success=False)
        raise HTTPError(
            HTTPStatus.NOT_FOUND,
            message=message,
        )

    # TODO: request just these three fields from the DB, instead of fetching
    # the full records, then slicing and sorting

    profile_metadata = []
    for profile in valid_profiles:
        profile_metadata.append(
            {
                "captured_date": profile.captured_date,
                "id": profile.id,
                "system_id": profile.inventory_id,
            }
        )
    sorted_profile_metadata = sorted(
        profile_metadata, key=lambda p: p["captured_date"], reverse=True
    )

    result = {"profiles": sorted_profile_metadata}
    return {"data": [result]}


@section.before_app_request
def ensure_account_number():
    return view_helpers.ensure_account_number(request, current_app.logger)


@section.before_app_request
def ensure_rbac():
    return view_helpers.ensure_has_permission(
        permissions=["drift:*:*", "drift:historical-system-profiles:read"],
        application="drift",
        app_name="historical-system-profiles",
        request=request,
        logger=current_app.logger,
        request_metric=metrics.rbac_requests,
        exception_metric=metrics.rbac_exceptions,
    )


def _get_event_counters():
    """
    small helper to create a dict of event counters
    """
    return {
        "systems_compared_no_sysprofile": metrics.inventory_no_sysprofile,
        "inventory_service_requests": metrics.inventory_requests,
        "inventory_service_exceptions": metrics.inventory_exceptions,
    }
