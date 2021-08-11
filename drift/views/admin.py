from flask import Blueprint, current_app, request
from kerlescan.service_interface import get_key_from_headers

from drift.baseline_service_interface import call_baseline_admin_svc


section = Blueprint("internal_admin", __name__)


@section.before_app_request
def status():
    auth_key = get_key_from_headers(request.headers)
    result = call_baseline_admin_svc(
        endpoint="status", service_auth_key=auth_key, logger=current_app.logger
    )
    return result
