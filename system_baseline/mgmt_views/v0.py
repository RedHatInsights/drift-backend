from flask import jsonify, current_app, request

from kerlescan.metrics_registry import get_registry
from system_baseline.models import SystemBaseline, db
from system_baseline import metrics as baseline_metrics

from prometheus_client import generate_latest

from sqlalchemy.sql import text

RANGES = text(
    "select count(*) from"
    " (select count(account) from system_baselines group by account) x"
    " where count between :low and :high"
)

BIGINT_MAX = 9223372036854775807


def _update_baseline_counts():
    """
    The baseline counts are updated when metrics are fetched via SQL
    """
    total_baselines = SystemBaseline.query.count()
    total_accounts = SystemBaseline.query.distinct(SystemBaseline.account.name).count()

    message = "counted baselines"
    current_app.logger.audit(message, request=request, success=True)

    total_accounts_ones = db.engine.execute(RANGES, low=0, high=10).scalar()
    total_accounts_tens = db.engine.execute(RANGES, low=10, high=100).scalar()
    total_accounts_hundred_plus = db.engine.execute(
        RANGES, low=100, high=BIGINT_MAX
    ).scalar()

    baseline_metrics.baseline_count.set(total_baselines)
    baseline_metrics.baseline_account_count.set(total_accounts)
    baseline_metrics.baseline_account_count_ones.set(total_accounts_ones)
    baseline_metrics.baseline_account_count_tens.set(total_accounts_tens)
    baseline_metrics.baseline_account_count_hundred_plus.set(
        total_accounts_hundred_plus
    )


def metrics():
    _update_baseline_counts()
    registry = get_registry()
    prometheus_data = generate_latest(registry)
    return prometheus_data


def status():
    return jsonify({"status": "running"})
