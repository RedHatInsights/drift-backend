from flask import Blueprint, jsonify, request
from http import HTTPStatus

from drift import info_parser
from drift.exceptions import HTTPError
from drift.inventory_service_interface import fetch_hosts, get_key_from_headers

APP_URL_PREFIX = "/r/insights/platform/drift"
API_VERSION_PREFIX = "/v0"

section = Blueprint('v0', __name__, url_prefix=APP_URL_PREFIX + API_VERSION_PREFIX)


@section.route("/compare")
def compare():
    host_ids = request.args.getlist('host_ids[]')
    auth_key = get_key_from_headers(request.headers)

    if not host_ids:
        raise HTTPError(HTTPStatus.BAD_REQUEST, message='host_ids[] not specified')

    if auth_key is None:
        raise HTTPError(HTTPStatus.BAD_REQUEST, message="auth header not specified")

    comparisons = info_parser.build_comparisons(fetch_hosts(host_ids, auth_key))
    return jsonify(comparisons)


@section.route("/status")
def status():
    return jsonify({'status': "running"})
