import datetime

from flask import Blueprint, request, current_app
from dateutil.relativedelta import relativedelta

from kerlescan import view_helpers
from kerlescan.inventory_service_interface import fetch_systems_with_profiles
from kerlescan.service_interface import get_key_from_headers

from historical_system_profiles import metrics, db_interface, config


section = Blueprint("v1", __name__)


def get_version():
    """
    return the service version
    """
    return {"version": "0.0.1"}


def _get_current_names_for_profiles(hsps):
    # make a unique list of inventory IDs
    inventory_ids = list({str(h.inventory_id) for h in hsps})

    auth_key = get_key_from_headers(request.headers)

    systems = fetch_systems_with_profiles(
        inventory_ids, auth_key, current_app.logger, _get_event_counters(),
    )
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


def get_hsps_by_ids(profile_ids):
    """
    return a list of historical system profiles for the given profile IDs
    """
    account_number = view_helpers.get_account_number(request)

    result = db_interface.get_hsps_by_profile_ids(profile_ids, account_number)
    filtered_result = _filter_old_hsps(result)

    result_with_updated_names = _get_current_names_for_profiles(filtered_result)

    return {"data": [r.to_json() for r in result_with_updated_names]}


def get_hsps_by_inventory_id(inventory_id):
    """
    return a list of historical system profiles for a given inventory id
    """
    account_number = view_helpers.get_account_number(request)
    query_results = db_interface.get_hsps_by_inventory_id(inventory_id, account_number)
    valid_profiles = _filter_old_hsps(query_results)

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
    return view_helpers.ensure_has_role(
        role="drift:*:*",
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
