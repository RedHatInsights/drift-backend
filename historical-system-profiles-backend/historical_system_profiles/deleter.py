import json
import time

from base64 import b64encode

from historical_system_profiles import db_interface
from historical_system_profiles import listener_metrics as metrics
from historical_system_profiles import probes
from historical_system_profiles.baseline_service_interface import (
    delete_system_baseline_associations,
)


def _delete_profiles(data, ptc, logger):
    """
    delete all profiles for the inventory ID in the message
    """
    inventory_id = data.value["id"]
    request_id = data.value["request_id"]
    account = data.value["account"]
    org_id = data.value["org_id"]

    _record_recv_message(request_id, inventory_id, account, org_id, ptc)
    db_interface.delete_hsps_by_inventory_id(inventory_id)

    # we don't have identity information in kafka message about deleting the system
    # so we need to create identity as a System
    # user.username and account_number is needed for kerlescan logging functions to work
    identity = {
        "identity": {
            "type": "System",
            "user": {"username": "HSPs deleter"},
            "account_number": account,
            "org_id": org_id,
        }
    }
    service_auth_key = b64encode(json.dumps(identity).encode("utf-8"))

    delete_system_baseline_associations(inventory_id, service_auth_key, logger)

    logger.info("deleted profiles for inventory_id %s" % inventory_id)
    _record_success_message(request_id, inventory_id, account, org_id, ptc)


def _record_recv_message(request_id, inventory_id, account, org_id, ptc):
    metrics.delete_messages_consumed.inc()
    ptc.emit_received_message(
        "received inventory delete event",
        request_id=request_id,
        account=account,
        org_id=org_id,
        inventory_id=inventory_id,
    )


def _record_success_message(request_id, inventory_id, account, org_id, ptc):
    metrics.delete_messages_processed.inc()
    ptc.emit_success_message(
        "deleted profiles for inventory record",
        request_id=request_id,
        account=account,
        org_id=org_id,
        inventory_id=inventory_id,
    )


def _emit_delete_error(data, ptc):
    """
    send an error message to payload tracker. This does not raise an
    exception.
    """
    metrics.delete_messages_errored.inc()
    inventory_id = data.value["id"]
    request_id = data.value["request_id"]
    account = data.value["account"]
    org_id = data.value["org_id"]
    ptc.emit_error_message(
        "error when deleting profiles for inventory record",
        request_id=request_id,
        account=account,
        org_id=org_id,
        inventory_id=inventory_id,
    )


def event_loop(flask_app, consumer, ptc, logger, delay_seconds):
    with flask_app.app_context():
        probes._update_readiness_state()
        while True:
            time.sleep(delay_seconds)
            probes._update_liveness_state()
            for data in consumer:
                try:
                    logger.debug(("kafka message recieved: '%s'", str(data)))
                    if data.value["type"] == "delete":
                        _delete_profiles(data, ptc, logger)
                except Exception:
                    _emit_delete_error(data, ptc)
                    logger.exception("An error occurred during message processing")
