from flask import jsonify

from drift.metrics_registry import get_registry

from prometheus_client import generate_latest


def metrics():
    registry = get_registry()
    prometheus_data = generate_latest(registry)
    return prometheus_data


def status():
    return jsonify({'status': "running"})
