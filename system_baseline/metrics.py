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
