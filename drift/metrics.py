from prometheus_client import Counter, Histogram


inventory_service_exceptions = Counter(
    "drift_inventory_service_exceptions", "count of exceptions raised by inv service"
)

baseline_service_exceptions = Counter(
    "drift_baseline_service_exceptions",
    "count of exceptions raised by baseline service",
)

hsp_service_exceptions = Counter(
    "drift_hsp_service_exceptions", "count of exceptions raised by HSP service"
)
rbac_exceptions = Counter("drift_rbac_exceptions", "count of exceptions raised by rbac service")

api_exceptions = Counter("drift_api_exceptions", "count of exceptions raised on public API")

systems_compared = Histogram(
    "drift_systems_compared",
    "count of systems compared in each request",
    buckets=[2, 4, 8, 16, 32, 64, 128, 256],
)

systems_compared_no_sysprofile = Histogram(
    "drift_systems_compared_no_sysprofile",
    "count of systems without system profile" "compared in each request",
    buckets=[2, 4, 8, 16, 32, 64, 128, 256],
)

comparison_report_requests = Histogram(
    "drift_comparison_report_requests", "comparison report request stats"
)

baseline_service_requests = Histogram(
    "drift_baseline_service_requests", "baseline service call stats"
)

hsp_service_requests = Histogram("drift_hsp_service_requests", "HSP service call stats")

rbac_requests = Histogram("drift_rbac_service_requests", "rbac service call stats")

inventory_service_requests = Histogram(
    "drift_inventory_service_requests", "inventory service call stats"
)

performance_timing = Histogram(
    "drift_performance_timing", "timing of code execution in drift app", ("method", "method_part")
)
