from prometheus_client import Counter, Histogram

rbac_requests = Histogram("hsp_rbac_service_requests", "rbac service call stats")
rbac_exceptions = Counter(
    "hsp_rbac_exceptions", "count of exceptions raised by rbac service"
)
