from calendar import monthrange
from datetime import date, timedelta

from flask import Blueprint, jsonify
from sqlalchemy import func

from system_baseline.models import SystemBaseline
from system_baseline.version import app_version
from system_baseline.views.v1 import _get_total_available_baselines


section = Blueprint("internal_admin", __name__)


def status():
    dt = date.today()

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

    result = {
        "system_baseline_version": app_version,
        "totalBaselinesCount": _get_total_available_baselines(),
        "customerIdsCount": customer_count,
        # "BaselinesBuckets": {"1": 206, "2": 46, "3": 11, "4": 4, "10+": 7, "5-10": 5},
        "createdBaselinesToday": created_baselines_today,
        "createdBaselinesWeek": created_baselines_week,
        "createdBaselinesMonth": created_baselines_month,
        # "totalBaselinesWithAssociationsCount": 25,
        # "BaselinesAssociationsBuckets": {"1": 19, "2": 4, "3": 1, "4": 1, "10+": 0, "5-10": 0},
    }

    return jsonify(result)
