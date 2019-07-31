import os
from flask import g

from prometheus_client import CollectorRegistry, multiprocess

from kerlescan.config import prometheus_multiproc_dir


def get_registry():
    """
    obtain a metrics registry. If one doesn't already exist, initialize and
    throw it into the global app context.
    """
    if "metrics_registry" not in g:
        g.metrics_registry = CollectorRegistry()
        multiprocess.MultiProcessCollector(g.metrics_registry)
    return g.metrics_registry


def create_prometheus_registry_dir():
    """
    create a registry dir. If one already exists, keep moving along.
    """
    if prometheus_multiproc_dir is None:
        raise Exception("prometheus_multiproc_dir not set")
    try:
        os.mkdir(prometheus_multiproc_dir)
    except FileExistsError:
        pass
