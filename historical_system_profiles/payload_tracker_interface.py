import json
from historical_system_profiles import config
from kafka import KafkaProducer
from kafka.errors import KafkaError

from datetime import datetime, timezone


class PayloadTrackerClient:
    def __init__(self, logger):
        self.logger = logger
        self.producer = self._init_producer()

    def _init_producer(self):
        producer = KafkaProducer(
            bootstrap_servers=config.bootstrap_servers,
            value_serializer=lambda x: json.dumps(x).encode("utf-8"),
        )
        return producer

    def emit_received_message(self, message, payload_id):
        message = self._create_message("received", message, payload_id)
        self._send_tracker_message(message)

    def emit_success_message(self, message, payload_id):
        message = self._create_message("success", message, payload_id)
        self._send_tracker_message(message)

    def emit_error_message(self, message, payload_id):
        message = self._create_message("error", message, payload_id)
        self._send_tracker_message(message)

    def _send_tracker_message(self, message):
        try:
            future = self.producer.send(config.tracker_topic, value=message)
            # get the result. This will raise an exception if the send failed.
            future.get(timeout=10)
        except KafkaError:
            self.logger.exception(
                "unable to send update on %s to tracker topic" % message["payload_id"]
            )

    def _create_message(self, status, message, payload_id):
        now = datetime.now(timezone.utc).isoformat()
        message = {
            "payload_id": payload_id,
            "service": "hsp-%s" % config.listener_type.lower(),
            "status": status,
            "status_msg": message,
            "date": now,
        }
        return message
