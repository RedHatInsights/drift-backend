from prometheus_client import Counter, Histogram

api_exceptions = Counter("drift_inventory_service_exceptions",
                         "count of exceptions raised on public API")

comparison_report_requests = Histogram("drift_comparison_report_requests",
                                       "comparison report request stats")

inventory_service_requests = Histogram("drift_inventory_service_requests",
                                       "inventory service call stats")
