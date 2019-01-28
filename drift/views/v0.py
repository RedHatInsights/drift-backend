from flask import Blueprint, current_app, jsonify, request

from drift.views.phony_data import PHONY_DATA

APP_URL_PREFIX = "/r/insights/platform/drift"
API_VERSION_PREFIX = "/v0"

section = Blueprint('v0', __name__, url_prefix=APP_URL_PREFIX + API_VERSION_PREFIX)


@section.route("/compare")
def compare():
    if 'X-RH-IDENTITY' in request.headers:
        current_app.logger.debug("X-RH-IDENTITY received")
    return jsonify(PHONY_DATA)


@section.route("/status")
def status():
    return jsonify({'status': "running"})
