from flask import Blueprint, request, current_app, Response
from http import HTTPStatus
import logging
import json
import base64

from system_baseline import metrics
from system_baseline.models import SystemBaseline, db
from system_baseline.constants import AUTH_HEADER_NAME
from system_baseline.exceptions import HTTPError

section = Blueprint("v0", __name__)


def _build_paginated_baseline_list_response(
    total, page, per_page, baseline_list, withhold_facts=False
):
    json_baseline_list = [
        baseline.to_json(withhold_facts=withhold_facts) for baseline in baseline_list
    ]
    json_output = {
        "total": total,
        "count": len(baseline_list),
        "page": page,
        "per_page": per_page,
        "results": json_baseline_list,
    }

    return _build_json_response(json_output)


def _build_json_response(json_data, status=200):
    return Response(json.dumps(json_data), status=status, mimetype="application/json")


@metrics.baseline_fetch_requests.time()
@metrics.api_exceptions.count_exceptions()
def get_baselines_by_ids(baseline_ids, page=1, per_page=100):
    """
    return a list of baselines given their ID
    """
    account_number = _get_account_number()
    query = SystemBaseline.query.filter(
        SystemBaseline.account == account_number, SystemBaseline.id.in_(baseline_ids)
    )

    query = query.order_by(SystemBaseline.created_on, SystemBaseline.id)
    query_results = query.paginate(page, per_page)

    return _build_paginated_baseline_list_response(
        query_results.total, page, per_page, query_results.items, withhold_facts=False
    )


@metrics.baseline_delete_requests.time()
@metrics.api_exceptions.count_exceptions()
def delete_baselines_by_ids(baseline_ids):
    """
    delete a list of baselines given their ID
    """
    account_number = _get_account_number()
    query = SystemBaseline.query.filter(
        SystemBaseline.account == account_number, SystemBaseline.id.in_(baseline_ids)
    )
    query.delete(synchronize_session="fetch")
    db.session.commit()


@metrics.baseline_fetch_all_requests.time()
@metrics.api_exceptions.count_exceptions()
def get_baselines(page=1, per_page=100):
    """
    return a list of baselines given their ID
    """
    account_number = _get_account_number()
    query = SystemBaseline.query.filter(SystemBaseline.account == account_number)

    query = query.order_by(SystemBaseline.created_on, SystemBaseline.id)
    query_results = query.paginate(page, per_page)

    return _build_paginated_baseline_list_response(
        query_results.total, page, per_page, query_results.items, withhold_facts=True
    )


@metrics.baseline_create_requests.time()
@metrics.api_exceptions.count_exceptions()
def create_baseline(system_baselines_list):
    """
    create a baseline
    """

    account_number = _get_account_number()

    created_baselines = []
    for input_baseline in system_baselines_list:
        baseline = SystemBaseline(
            account=account_number,
            display_name=input_baseline["display_name"],
            baseline_facts=input_baseline["baseline_facts"],
        )
        db.session.add(baseline)
        db.session.commit()  # commit now so we get a created/updated time before json conversion
        created_baselines.append(baseline.to_json())

    return created_baselines


def _merge_baselines(baseline, baseline_updates):
    """
    merge a baseline with a partial update set.
    """
    # convert to dicts for easier manipulation
    existing_facts = {fact["name"]: fact["value"] for fact in baseline.baseline_facts}
    new_facts = {
        fact["name"]: fact["value"] for fact in baseline_updates["baseline_facts"]
    }

    existing_facts.update(new_facts)

    # convert back
    merged_baseline_facts = []
    for fact in existing_facts:
        baseline_fact = {"name": fact, "value": existing_facts[fact]}
        merged_baseline_facts.append(baseline_fact)

    baseline.baseline_facts = merged_baseline_facts
    return baseline


def update_baseline(baseline_ids, system_baseline_partial):
    """
    update a baseline
    """
    if len(baseline_ids) > 1:
        raise "can only patch one baseline at a time"

    account_number = _get_account_number()
    query = SystemBaseline.query.filter(
        SystemBaseline.account == account_number, SystemBaseline.id == baseline_ids[0]
    )
    existing_baseline = query.first_or_404()

    new_baseline = _merge_baselines(existing_baseline, system_baseline_partial)
    db.session.add(new_baseline)
    db.session.commit()

    # pull baseline again so we have the correct updated timestamp and fact count
    query = SystemBaseline.query.filter(
        SystemBaseline.account == account_number, SystemBaseline.id == baseline_ids[0]
    )
    return [query.first().to_json()]


def _get_account_number():
    auth_key = get_key_from_headers(request.headers)
    identity = json.loads(base64.b64decode(auth_key))["identity"]
    return identity["account_number"]


def _is_mgmt_url(path):
    """
    small helper to test if URL is for management API.
    """
    return path.startswith("/mgmt/")


def _is_openapi_url(path):
    """
    small helper to test if URL is the openapi spec
    """
    return path == "/api/system_baseline/v0/openapi.json"


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


def get_key_from_headers(incoming_headers):
    """
    return auth key from header
    """
    return incoming_headers.get(AUTH_HEADER_NAME)
