from calendar import monthrange
from datetime import date, timedelta

from flask import Blueprint, jsonify
from sqlalchemy import func

from system_baseline.models import SystemBaseline, SystemBaselineMappedSystem
from system_baseline.version import app_version


section = Blueprint("internal_admin", __name__)


def status():
    dt = date.today()

    total_baselines = SystemBaseline.query.with_entities(SystemBaseline.id).distinct().count()
    customer_count = SystemBaseline.query.with_entities(SystemBaseline.account).distinct().count()

    created_baselines_today = SystemBaseline.query.filter(
        func.date(SystemBaseline.created_on) == dt
    ).count()

    created_baselines_week = SystemBaseline.query.filter(
        SystemBaseline.created_on.between(dt - timedelta(days=dt.weekday()), dt + timedelta(days=6))
    ).count()

    created_baselines_month = SystemBaseline.query.filter(
        SystemBaseline.created_on.between(
            dt.replace(day=1), dt.replace(day=monthrange(dt.year, dt.month)[1])
        )
    ).count()

    baseline_bucket_counts = {}

    for i in range(1, 5):
        baseline_bucket_counts[i] = (
            SystemBaseline.query.with_entities(SystemBaseline.account)
            .group_by(SystemBaseline.account)
            .having(func.count() == i)
        ).count()

    baseline_bucket_counts[5] = (
        SystemBaseline.query.with_entities(SystemBaseline.account)
        .group_by(SystemBaseline.account)
        .having(func.count() >= 5)
        .having(func.count() <= 10)
    ).count()

    baseline_bucket_counts[11] = (
        SystemBaseline.query.with_entities(SystemBaseline.account)
        .group_by(SystemBaseline.account)
        .having(func.count() > 10)
    ).count()

    baselines_with_associations = (
        (SystemBaselineMappedSystem.query.with_entities(SystemBaselineMappedSystem.system_id))
        .distinct()
        .count()
    )

    result = {
        "system_baseline_version": app_version,
        "totalBaselinesCount": total_baselines,
        "customerIdsCount": customer_count,
        "BaselinesBuckets": {
            "1": baseline_bucket_counts[1],
            "2": baseline_bucket_counts[2],
            "3": baseline_bucket_counts[3],
            "4": baseline_bucket_counts[4],
            "10+": baseline_bucket_counts[5],
            "5-10": baseline_bucket_counts[11],
        },
        "createdBaselinesToday": created_baselines_today,
        "createdBaselinesWeek": created_baselines_week,
        "createdBaselinesMonth": created_baselines_month,
        "totalBaselinesWithAssociationsCount": baselines_with_associations,
    }

    return jsonify(result)
