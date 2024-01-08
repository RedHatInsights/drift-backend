from pathlib import Path

from historical_system_profiles import config


def _update_liveness_state():
    # touches liveness probe file
    Path(config.liveness_probe_filepath).touch(exist_ok=True)


def _update_readiness_state():
    # touches readiness probe file
    Path(config.readiness_probe_filepath).touch(exist_ok=True)
