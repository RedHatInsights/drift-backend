import json

from datetime import datetime, timezone
from kafka import KafkaProducer

from historical_system_profiles import config


EVENT_DRIFT_BASELINE_DETECTED = "drift-baseline-detected"


class NotificationServiceInterface:
    """Client API for sending events to Notification Service"""

    def __init__(self, logger):
        self.initialized = False
        self.logger = logger

        self.notification_service_topic = config.notification_service_topic
        self.notification_bundle = config.notification_bundle
        self.notification_app = config.notification_app
        if self.notification_service_topic:
            self.logger.info(
                f"Initializing NotificationServiceInterface - with "
                f"{'secure' if config.enable_kafka_ssl else 'normal'} producer "
                f"on topic '{self.notification_service_topic}' using "
                f"bundle '{self.notification_bundle}' and "
                f"app '{self.notification_app}'"
            )
            if config.enable_kafka_ssl:
                self.producer = KafkaProducer(
                    bootstrap_servers=config.bootstrap_servers,
                    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                    security_protocol="SSL",
                    ssl_cafile=config.kafka_ssl_cert,
                    ssl_check_hostname=False,
                )
            else:
                self.producer = KafkaProducer(
                    bootstrap_servers=config.bootstrap_servers,
                    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                )
            self.initialized = True
        if not self.initialized:
            self.logger.warning("NotificationServiceInterface not initialized.")

    def send_notification(self, event):
        if not self.initialized:
            self.logger.warning("NotificationServiceInterface not initialized.")
            return
        self.producer.send(self.notification_service_topic, event.message)
        self.logger.audit("Sent baseline drift notification message", success=True)


class _NotificationEventBase:
    """Base event on which all notification events are built"""

    def __init__(self, event_type, account_id, context={}):
        self.message = {
            "bundle": self.notification_bundle,
            "application": self.notification_app,
            "event_type": event_type,
            "timestamp": datetime.utcnow().replace(tzinfo=timezone.utc).isoformat(),
            "account_id": account_id,
            "events": [],
            "context": json.dumps(context).encode("utf-8"),
        }

    def _add_event(self, payload):
        self.message["events"].append(
            {"metadata": {}, "payload": json.dumps(payload).encode("utf-8")}
        )


class EventDriftBaselineDetected(_NotificationEventBase):
    """Message for drift-baseline-detected notification event"""

    def __init__(self, account_id, insights_id, system_check_in, display_name, tags=[]):
        context = {
            "insights_id": insights_id,
            "system_check_in": system_check_in,
            "display_name": display_name,
            "tags": tags,
        }
        super(EventDriftBaselineDetected, self).__init__(
            EVENT_DRIFT_BASELINE_DETECTED, account_id, context
        )

    def add_drifted_baseline(self, baseline_id, baseline_name, facts):
        payload = {
            "baseline_id": baseline_id,
            "baseline_name": baseline_name,
        }
        super(EventDriftBaselineDetected, self)._add_event(payload)
