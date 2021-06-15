from flask import Blueprint, request, current_app

from kerlescan import view_helpers
from kerlescan.view_helpers import validate_uuids

from system_baseline import metrics
from system_baseline.version import app_version
from system_baseline.models import SystemBaselineMappedSystem

section = Blueprint("v1", __name__)

FACTS_MAXSIZE = 2 ** 19  # 512KB


def get_version():
    """
    return the service version
    """
    return {"version": app_version}


@metrics.baseline_fetch_all_requests.time()
@metrics.api_exceptions.count_exceptions()
def get_baselines_by_system_id(system_id=None):
    account_number = view_helpers.get_account_number(request)

    if system_id:
        validate_uuids([system_id])
        query = SystemBaselineMappedSystem.query.filter(
            SystemBaselineMappedSystem.account == account_number,
            SystemBaselineMappedSystem.system_id == system_id,
        )
    else:
        query = SystemBaselineMappedSystem.query.filter(
            SystemBaselineMappedSystem.account == account_number
        )

    try:
        query_results = query.all()
    except Exception:
        message = "Unknown error when reading baselines by system id"
        current_app.logger.audit(message, request=request, success=False)
        raise

    message = "read baselines with system"
    current_app.logger.audit(message, request=request, success=True)

    return [result.system_baseline_id for result in query_results]


@metrics.baseline_delete_requests.time()
@metrics.api_exceptions.count_exceptions()
def delete_systems_by_ids(system_ids):
    """
    delete a list of systems given their system IDs as a list
    """
    validate_uuids(system_ids)
    account_number = view_helpers.get_account_number(request)
    try:
        SystemBaselineMappedSystem.delete_by_system_ids(system_ids, account_number)
    except Exception:
        message = "Unknown error when deleting systems by ids"
        current_app.logger.audit(message, request=request, success=False)
        raise

    message = "delete systems by ids"
    current_app.logger.audit(message, request=request, success=True)

    return "OK"
