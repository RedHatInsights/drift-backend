import time

from historical_system_profiles import db_interface
from historical_system_profiles import listener_metrics as metrics


def _delete_profiles(data, ptc, logger):
    """
    delete all profiles for the inventory ID in the message
    """
    inventory_id = data.value["id"]
    request_id = data.value["request_id"]
    account = data.value["account"]

    _record_recv_message(request_id, inventory_id, account, ptc)
    db_interface.delete_hsps_by_inventory_id(inventory_id)
    logger.info("deleted profiles for inventory_id %s" % inventory_id)
    _record_success_message(request_id, inventory_id, account, ptc)


def _record_recv_message(request_id, inventory_id, account, ptc):
    metrics.delete_messages_consumed.inc()
    ptc.emit_received_message(
        "received inventory delete event",
        request_id=request_id,
        account=account,
        inventory_id=inventory_id,
    )


def _record_success_message(request_id, inventory_id, account, ptc):
    metrics.delete_messages_processed.inc()
    ptc.emit_success_message(
        "deleted profiles for inventory record",
        request_id=request_id,
        account=account,
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
    ptc.emit_error_message(
        "error when deleting profiles for inventory record",
        request_id=request_id,
        account=account,
        inventory_id=inventory_id,
    )


def event_loop(flask_app, consumer, ptc, logger, delay_seconds):
    with flask_app.app_context():
        while True:
            time.sleep(delay_seconds)
            for data in consumer:
                try:
                    if data.value["type"] == "delete":
                        _delete_profiles(data, ptc, logger)
                except Exception:
                    _emit_delete_error(data, ptc)
                    logger.exception("An error occurred during message processing")
