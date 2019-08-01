from prometheus_client import Counter, Histogram

api_exceptions = Counter(
    "system_baseline_api_exceptions", "count of exceptions raised on public API"
)

baseline_create_requests = Histogram(
    "baseline_create_requests", "baseline create request stats"
)

baseline_fetch_requests = Histogram(
    "baseline_fetch_requests", "baseline fetch request stats"
)

baseline_fetch_all_requests = Histogram(
    "baseline_fetch_all_requests", "baseline fetch all request stats"
)

baseline_delete_requests = Histogram(
    "baseline_delete_requests", "baseline delete request stats"
)

inventory_service_requests = Histogram(
    "drift_inventory_service_requests", "inventory service call stats"
)

inventory_service_exceptions = Counter(
    "drift_inventory_service_exceptions", "count of exceptions raised by inv service"
)

systems_compared_no_sysprofile = Histogram(
    "drift_systems_compared_no_sysprofile",
    "count of systems without system profile" "compared in each request",
    buckets=[2, 4, 8, 16, 32, 64, 128, 256],
)
