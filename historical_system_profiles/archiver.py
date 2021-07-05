import time

from historical_system_profiles import db_interface
from historical_system_profiles import listener_metrics as metrics
from historical_system_profiles.baseline_service_interface import fetch_system_baseline_associations
from historical_system_profiles.drift_service_interface import check_for_drift
from historical_system_profiles.notification_service_interface import (
    EventDriftBaselineDetected,
    NotificationServiceInterface,
)


def _record_recv_message(host, request_id, ptc):
    metrics.profile_messages_consumed.inc()
    ptc.emit_received_message(
        "received inventory update event",
        request_id=request_id,
        account=host["account"],
        inventory_id=host["id"],
    )


def _record_success_message(hsp_id, host, request_id, ptc):
    metrics.profile_messages_processed.inc()
    ptc.emit_success_message(
        "stored historical profile %s" % hsp_id,
        request_id=request_id,
        account=host["account"],
        inventory_id=host["id"],
    )


def _record_duplicate_message(host, request_id, ptc):
    metrics.profile_messages_processed_duplicates.inc()
    ptc.emit_success_message(
        "profile not saved to db (timestamp already exists)",
        request_id=request_id,
        account=host["account"],
        inventory_id=host["id"],
    )


def _archive_profile(data, ptc, logger, notification_service):
    """
    given an event, archive a profile and emit a success message
    """

    if not data.value or not isinstance(data.value, dict):
        logger.info("skipping message where data.value is empty or not a dict")
        return

    if "type" not in data.value:
        logger.info("skipping message that does not have a type")
        return

    if data.value["type"] not in ("created", "updated"):
        logger.info("skipping message that is not created or updated type")
        return

    service_auth_key = None
    if "platform_metadata" in data.value and isinstance(data.value["platform_metadata"], dict):
        service_auth_key = data.value["platform_metadata"].get("b64_identity", None)

    host = data.value["host"]
    request_id = _get_request_id(data)
    _record_recv_message(host, request_id, ptc)

    profile = host["system_profile"]
    # fqdn is on the host but we need it in the profile as well
    profile["fqdn"] = host["fqdn"]

    # tags is on the host but we need it in the profile as well
    profile["tags"] = host["tags"]

    captured_date = profile.get("captured_date")
    account = host["account"]

    # Historical profiles have a "captured_date" which is when the data was
    # taken from the system by insights-client. However, some reporters to
    # inventory service run in a batch mode and do not update the
    # captured_date. The logic below will only save a profile if the
    # captured_date is one that we don't already have for the system in
    # question.  This works for our purposes since users differentiate between
    # profiles in the app via captured_date.

    if captured_date and db_interface.is_profile_recorded(captured_date, host["id"], account):
        logger.info("profile with date %s is already recorded for %s" % (captured_date, host["id"]))
        _record_duplicate_message(host, request_id, ptc)
    else:
        hsp = db_interface.create_profile(
            inventory_id=host["id"],
            profile=profile,
            account_number=host["account"],
        )
        _record_success_message(hsp.id, host, request_id, ptc)
        logger.info(
            "wrote %s to historical database (inv id: %s, captured_on: %s)"
            % (hsp.id, hsp.inventory_id, hsp.captured_on)
        )
        # After the new hsp is saved, we need to check for any reason to alert via
        # triggering a notification, i.e. if drift from any associated baselines has
        # occurred.
        _check_and_send_notifications(
            host["id"],
            host["account"],
            host["updated"],
            host["display_name"],
            host["tags"],
            notification_service,
            service_auth_key,
            logger,
        )


def _check_and_send_notifications(
    inventory_id,
    account_id,
    system_check_in,
    display_name,
    tags,
    notification_service,
    service_auth_key,
    logger,
):
    # After the new hsp is saved, we need to check for any reason to alert Notifications
    # First, check if this system id is associated with any baselines
    # If yes, then for each baseline associated, call for a short-circuited comparison
    # to see if the system has drifted from that baseline.
    # If anything has changed, send a kafka message to trigger a notification.

    baseline_ids = fetch_system_baseline_associations(inventory_id, service_auth_key, logger)
    # If yes, then for each baseline associated, call for a short-circuited comparison
    # to see if the system has drifted from that baseline.
    if baseline_ids:
        drift_found = False
        event = EventDriftBaselineDetected(
            account_id, inventory_id, system_check_in, display_name, tags
        )
        for baseline_id in baseline_ids:
            comparison = check_for_drift(inventory_id, baseline_id, service_auth_key, logger)
            if comparison["drift_event_notify"]:
                # If anything has changed, send a kafka message to trigger a notification.
                # Add each baseline to our event, then send notification only once
                # containing the whole list of events for this system
                drift_found = True
                # currently using baseline_id in place of baseline_name for testing
                # will need to make another call to api to get this later
                event.add_drifted_baseline(baseline_id, baseline_id, comparison)
                logger.info(
                    "drift detected, baseline added to event baseline id: %s)" % (baseline_id)
                )
        if drift_found:
            notification_service.send_notification(event)
            logger.info(
                "drift detected, signal sent for Notifications to send alert inv id: %s)"
                % (inventory_id)
            )


def _get_request_id(data):
    """
    small helper to fetch request ID off a message
    """
    # if platform_metadata is not None, and it has a request_id, use it. Otherwise, -1.
    platform_metadata = data.value["platform_metadata"]
    request_id = -1
    if platform_metadata:
        request_id = platform_metadata.get("request_id", -1)
    return request_id


def _emit_archiver_error(data, ptc, logger):
    """
    send an error message to payload tracker. This does not raise an
    exception.
    """
    metrics.profile_messages_errored.inc()
    host = data.value["host"]
    request_id = _get_request_id(data)
    ptc.emit_error_message(
        "error when storing historical profile",
        request_id=request_id,
        account=host["account"],
        inventory_id=host["id"],
    )
    logger.exception("An error occurred during message processing")


def event_loop(flask_app, consumer, ptc, logger, delay_seconds):
    with flask_app.app_context():
        notification_service = NotificationServiceInterface(logger)
        while True:
            time.sleep(delay_seconds)
            for data in consumer:
                try:
                    logger.debug(("kafka message recieved: '%s'", str(data)))
                    _archive_profile(data, ptc, logger, notification_service)
                except Exception:
                    _emit_archiver_error(data, ptc, logger)
