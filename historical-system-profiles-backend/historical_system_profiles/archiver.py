import base64
import json
import time

from kerlescan.inventory_service_interface import filter_out_systems
from kerlescan.system_baseline_service_interface import update_mapped_system_groups

from historical_system_profiles import db_interface, listener_metrics, metrics, probes
from historical_system_profiles.baseline_service_interface import (
    fetch_baselines,
    fetch_system_baseline_associations,
)
from historical_system_profiles.drift_service_interface import check_for_drift
from historical_system_profiles.notification_service_interface import (
    EventDriftBaselineDetected,
    NotificationServiceInterface,
)


def _record_recv_message(host, request_id, ptc):
    listener_metrics.profile_messages_consumed.inc()
    ptc.emit_received_message(
        "received inventory update event",
        request_id=request_id,
        account=host["account"] if "account" in host else None,
        org_id=host["org_id"],
        inventory_id=host["id"],
    )


def _record_success_message(hsp_id, host, request_id, ptc):
    listener_metrics.profile_messages_processed.inc()
    ptc.emit_success_message(
        "stored historical profile %s" % hsp_id,
        request_id=request_id,
        account=host["account"] if "account" in host else None,
        org_id=host["org_id"],
        inventory_id=host["id"],
    )


def _record_duplicate_message(host, request_id, ptc):
    listener_metrics.profile_messages_processed_duplicates.inc()
    ptc.emit_success_message(
        "profile not saved to db (timestamp already exists)",
        request_id=request_id,
        account=host["account"] if "account" in host else None,
        org_id=host["org_id"],
        inventory_id=host["id"],
    )


def _filter_inventory_groups_data(groups):
    return [
        {key: group[key] for key in set(["id", "name"]) & set(group.keys())} for group in groups
    ]


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

    if not filter_out_systems([profile]):
        return

    # fqdn is on the host but we need it in the profile as well
    profile["fqdn"] = host["fqdn"]

    # tags is on the host but we need it in the profile as well
    tags = profile["tags"] = host["tags"]

    captured_date = profile.get("captured_date")
    inventory_id = host["id"]
    account = host.get("account")
    org_id = host["org_id"]
    groups = host.get("groups")

    if service_auth_key is None:
        service_auth_key_data = {"identity": {"org_id": org_id, "account": account}}
        service_auth_key = base64.b64encode(bytes(json.dumps(service_auth_key_data), "UTF-8"))

    baseline_ids = fetch_system_baseline_associations(inventory_id, service_auth_key, logger)

    if baseline_ids:
        # update groups in Baselines Associated System
        update_mapped_system_groups(
            inventory_id,
            groups,
            service_auth_key,
            logger,
            metrics.baseline_service_requests,
            metrics.baseline_service_exceptions,
        )

    # Historical profiles have a "captured_date" which is when the data was
    # taken from the system by insights-client. However, some reporters to
    # inventory service run in a batch mode and do not update the
    # captured_date. The logic below will only save a profile if the
    # captured_date is one that we don't already have for the system in
    # question.  This works for our purposes since users differentiate between
    # profiles in the app via captured_date.

    if captured_date and db_interface.is_profile_recorded(
        captured_date, inventory_id, account, org_id
    ):
        logger.info(
            "profile with date %s is already recorded for %s, using account id: %s, org_id: %s"
            % (captured_date, inventory_id, account, org_id)
        )
        _record_duplicate_message(host, request_id, ptc)
    else:
        # remove keys we do not care about
        if groups:
            groups = _filter_inventory_groups_data(groups)

        hsp = db_interface.create_profile(
            inventory_id=inventory_id,
            profile=profile,
            account_number=account,
            org_id=org_id,
            groups=groups,
        )
        _record_success_message(hsp.id, host, request_id, ptc)
        logger.info(
            "wrote %s to historical database (inv id: %s, captured_on: %s, account id: %s,"
            " org_id: %s)" % (hsp.id, hsp.inventory_id, hsp.captured_on, account, org_id)
        )
        # After the new hsp is saved, we need to check for any reason to alert via
        # triggering a notification, i.e. if drift from any associated baselines has
        # occurred.
        _check_and_send_notifications(
            inventory_id=inventory_id,
            baseline_ids=baseline_ids,
            account_id=account,
            org_id=org_id,
            system_check_in=host["updated"],
            display_name=host["display_name"],
            tags=tags,
            groups=groups,
            notification_service=notification_service,
            service_auth_key=service_auth_key,
            logger=logger,
        )


def _check_if_notification_enabled(baseline_id, service_auth_key, logger):
    return fetch_baselines([baseline_id], service_auth_key, logger)[0]["notifications_enabled"]


def _check_and_send_notifications(
    inventory_id,
    baseline_ids,
    account_id,
    org_id,
    system_check_in=None,
    display_name=None,
    tags=None,
    groups=None,
    notification_service=None,
    service_auth_key=None,
    logger=None,
):
    # After the new hsp is saved, we need to check for any reason to alert Notifications
    # First, check if this system id is associated with any baselines
    # If yes, then for each baseline associated, call for a short-circuited comparison
    # to see if the system has drifted from that baseline.
    # If anything has changed, send a kafka message to trigger a notification.

    # If yes, then for each baseline associated, call for a short-circuited comparison
    # to see if the system has drifted from that baseline.
    if baseline_ids:
        # check for Drift Event enabled, do a comparison and send notification
        drift_found = False
        event = EventDriftBaselineDetected(
            account_id, org_id, inventory_id, system_check_in, display_name, tags
        )
        for baseline_id in baseline_ids:
            if _check_if_notification_enabled(baseline_id, service_auth_key, logger):
                comparison = check_for_drift(inventory_id, baseline_id, service_auth_key, logger)
                if comparison["drift_event_notify"]:
                    # If anything has changed, send a kafka message to trigger a notification.
                    # Add each baseline to our event, then send notification only once
                    # containing the whole list of events for this system
                    drift_found = True
                    baseline_name = fetch_baselines([baseline_id], service_auth_key, logger)[0][
                        "display_name"
                    ]
                    event.add_drifted_baseline(baseline_id, baseline_name, comparison)
                    logger.info(
                        "drift detected, baseline added to event (baseline id: %s, account id: %s,"
                        " org_id: %s)" % (baseline_id, account_id, org_id)
                    )
        if drift_found:
            notification_service.send_notification(event)
            logger.info(
                """drift detected, signal sent for Notifications to send alert
                (inv id: %s, account id %s, org_id %s)"""
                % (inventory_id, account_id, org_id)
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
    listener_metrics.profile_messages_errored.inc()
    host = data.value["host"]
    request_id = _get_request_id(data)
    ptc.emit_error_message(
        "error when storing historical profile",
        request_id=request_id,
        account=host["account"] if "account" in host else None,
        org_id=host["org_id"],
        inventory_id=host["id"],
    )
    logger.exception("An error occurred during message processing")


def event_loop(flask_app, consumer, ptc, logger, delay_seconds):
    with flask_app.app_context():
        notification_service = NotificationServiceInterface(logger)
        probes._update_readiness_state()
        while True:
            time.sleep(delay_seconds)
            logger.debug("Event loop running")
            probes._update_liveness_state()
            for data in consumer:
                logger.debug("Data found, processing kafka message")
                try:
                    logger.debug(("kafka message recieved: '%s'", str(data)))
                    _archive_profile(data, ptc, logger, notification_service)
                except Exception:
                    _emit_archiver_error(data, ptc, logger)
