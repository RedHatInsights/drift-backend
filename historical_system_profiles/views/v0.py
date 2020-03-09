from flask import Blueprint, request, current_app

from kerlescan import view_helpers
from kerlescan.inventory_service_interface import fetch_systems_with_profiles
from kerlescan.service_interface import get_key_from_headers

from historical_system_profiles import metrics, db_interface


section = Blueprint("v0", __name__)


def get_version():
    """
    return the service version
    """
    return {"version": "0.0.1"}


def get_hsps_by_ids(profile_ids):
    """
    return a list of historical system profiles for the given profile IDs
    """
    account_number = view_helpers.get_account_number(request)

    result = db_interface.get_hsps_by_profile_ids(profile_ids, account_number)

    result_with_updated_names = _get_current_names_for_profiles(result)

    return {"data": [r.to_json() for r in result_with_updated_names]}


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


def get_hsps_by_inventory_id(inventory_id):
    """
    return a list of historical system profiles for a given inventory id
    """
    account_number = view_helpers.get_account_number(request)
    query_results = db_interface.get_hsps_by_inventory_id(inventory_id, account_number)

    result = {
        "profiles": [
            {"captured_date": p.captured_date, "id": p.id} for p in query_results
        ],
    }
    return {"data": [result]}


def create_profile(body):
    """
    return a list of historical system profiles for a given inventory id
    """
    account_number = view_helpers.get_account_number(request)

    profile = db_interface.create_profile(
        body["inventory_id"], body["profile"], account_number
    )

    return profile.to_json()


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
