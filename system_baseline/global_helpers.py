from flask import Blueprint, current_app, request
from kerlescan import view_helpers

from system_baseline import app_config, metrics


global_helpers_bp = Blueprint("global_helpers", __name__)


@global_helpers_bp.before_app_request
def log_username():
    view_helpers.log_username(current_app.logger, request)
    message = "logged username"
    current_app.logger.audit(message, request=request)


@global_helpers_bp.before_app_request
def ensure_entitled():
    return view_helpers.ensure_entitled(request, app_config.get_app_name(), current_app.logger)


@global_helpers_bp.before_app_request
def ensure_account_number():
    return view_helpers.ensure_account_number(request, current_app.logger)


@global_helpers_bp.before_app_request
def ensure_org_id():
    return view_helpers.ensure_org_id(request, current_app.logger)


@global_helpers_bp.before_app_request
def ensure_rbac_baselines_read():
    # permissions consist of a list of "or" permissions where any will work,
    # and each sublist is a set of "and" permissions that all must be true.
    # For example:
    # permissions=[["drift:*:*"], ["drift:notifications:read", "drift:baselines:read"]]
    # If we just have *:*, it works, but if not, we need both notifications:read and
    # baselines:read in order to allow access.
    return view_helpers.ensure_has_permission(
        permissions=[["drift:*:*"], ["drift:baselines:read"]],
        application="drift",
        app_name="system-baseline",
        request=request,
        logger=current_app.logger,
        request_metric=metrics.rbac_requests,
        exception_metric=metrics.rbac_exceptions,
    )


def ensure_rbac_baselines_write():
    # permissions consist of a list of "or" permissions where any will work,
    # and each sublist is a set of "and" permissions that all must be true.
    # For example:
    # permissions=[["drift:*:*"], ["drift:notifications:read", "drift:baselines:read"]]
    # If we just have *:*, it works, but if not, we need both notifications:read and
    # baselines:read in order to allow access.
    return view_helpers.ensure_has_permission(
        permissions=[["drift:*:*"], ["drift:baselines:write"]],
        application="drift",
        app_name="system-baseline",
        request=request,
        logger=current_app.logger,
        request_metric=metrics.rbac_requests,
        exception_metric=metrics.rbac_exceptions,
    )


def ensure_rbac_inventory_read():
    return view_helpers.ensure_has_permission(
        permissions=[
            ["inventory:*:*"],
            ["inventory:*:read"],
            ["inventory:hosts:*"],
            ["inventory:hosts:read"],
        ],
        application="inventory",
        app_name="system-baseline",
        request=request,
        logger=current_app.logger,
        request_metric=metrics.rbac_requests,
        exception_metric=metrics.rbac_exceptions,
    )


def ensure_rbac_notifications_read():
    # permissions consist of a list of "or" permissions where any will work,
    # and each sublist is a set of "and" permissions that all must be true.
    # For example:
    # permissions=[["drift:*:*"], ["drift:notifications:read", "drift:baselines:read"]]
    # If we just have *:*, it works, but if not, we need both notifications:read and
    # baselines:read in order to allow access.
    return view_helpers.ensure_has_permission(
        permissions=[
            ["drift:*:*"],
            ["drift:notifications:read", "drift:baselines:read"],
        ],
        application="drift",
        app_name="system_baseline",
        request=request,
        logger=current_app.logger,
        request_metric=metrics.rbac_requests,
        exception_metric=metrics.rbac_exceptions,
    )


def ensure_rbac_notifications_write():
    # permissions consist of a list of "or" permissions where any will work,
    # and each sublist is a set of "and" permissions that all must be true.
    # For example:
    # permissions=[["drift:*:*"], ["drift:notifications:read", "drift:baselines:read"]]
    # If we just have *:*, it works, but if not, we need both notifications:read and
    # baselines:read in order to allow access.
    return view_helpers.ensure_has_permission(
        permissions=[
            ["drift:*:*"],
            ["drift:notifications:write", "drift:baselines:read"],
        ],
        application="drift",
        app_name="system_baseline",
        request=request,
        logger=current_app.logger,
        request_metric=metrics.rbac_requests,
        exception_metric=metrics.rbac_exceptions,
    )


@global_helpers_bp.after_app_request
def ensure_hsts_response(response):
    """
    This method will insert HSTS header into all responses the server
    send to client
    """
    current_app.logger.debug("Including hsts header in response")

    response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"
    return response
