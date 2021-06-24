from flask import Blueprint, request, current_app

from kerlescan import view_helpers

from system_baseline import metrics, app_config


global_helpers_bp = Blueprint("global_helpers", __name__)


@global_helpers_bp.before_app_request
def log_username():
    view_helpers.log_username(current_app.logger, request)
    message = "logged username"
    current_app.logger.audit(message, request=request)


@global_helpers_bp.before_app_request
def ensure_entitled():
    return view_helpers.ensure_entitled(
        request, app_config.get_app_name(), current_app.logger
    )


@global_helpers_bp.before_app_request
def ensure_account_number():
    return view_helpers.ensure_account_number(request, current_app.logger)


@global_helpers_bp.before_app_request
def ensure_rbac_baselines_read():
    return view_helpers.ensure_has_permission(
        permissions=["drift:*:*", "drift:baselines:read"],
        application="drift",
        app_name="system-baseline",
        request=request,
        logger=current_app.logger,
        request_metric=metrics.rbac_requests,
        exception_metric=metrics.rbac_exceptions,
    )


def ensure_rbac_baselines_write():
    return view_helpers.ensure_has_permission(
        permissions=["drift:*:*", "drift:baselines:write"],
        application="drift",
        app_name="system-baseline",
        request=request,
        logger=current_app.logger,
        request_metric=metrics.rbac_requests,
        exception_metric=metrics.rbac_exceptions,
    )


def ensure_rbac_notifications_read():
    return view_helpers.ensure_has_permission(
        permissions=["drift:*:*", "drift:notifications:read", "drift:baselines:read"],
        application="drift",
        app_name="system_baseline",
        request=request,
        logger=current_app.logger,
        request_metric=metrics.rbac_requests,
        exception_metric=metrics.rbac_exceptions,
    )


def ensure_rbac_notifications_write():
    return view_helpers.ensure_has_permission(
        permissions=["drift:*:*", "drift:notifications:write", "drift:baselines:read"],
        application="drift",
        app_name="system_baseline",
        request=request,
        logger=current_app.logger,
        request_metric=metrics.rbac_requests,
        exception_metric=metrics.rbac_exceptions,
    )
