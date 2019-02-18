import os

# please ensure these are all documented in README.md
log_level = os.getenv('LOG_LEVEL', "INFO")
inventory_svc_hostname = os.getenv('INVENTORY_SVC_URL', "http://inventory_svc_url_is_not_set")
return_mock_data = os.getenv('RETURN_MOCK_DATA', False)
prometheus_multiproc_dir = os.getenv('prometheus_multiproc_dir', None)
