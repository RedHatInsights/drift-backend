# drift-backend
System drift analysis service

This is a flask app that provides an API for drift-frontend. It listens on port
8080 by default with gunicorn. Prometheus stats will be stored in a temp
directory.

To run:

`prometheus_multiproc_dir=/tmp/tempdir INVENTORY_SVC_URL=<inventory service url> run_app.sh`


To set the debug level (`info` by default):

`LOG_LEVEL=debug prometheus_multiproc_dir=/tmp/tempdir INVENTORY_SVC_URL=<inventory service url> run_app.sh`

You may also set `RETURN_MOCK_DATA` to `true` if you want a large set of mock
facts returned for each system.

The prometheus_multiproc_dir should be a path to a directory for sharing info
between app processes. If the dir does not already exist, the app will create
one.

The same info as above, but in handy table form:

| env var name              | required? | expected values | description                                       |
| ------------              | --------- | --------------- | ------------                                      |
| INVENTORY_SVC_URL         | yes       | URL             | URL for inventory service (do not include path)   |
| LOG_LEVEL                 | no        | string          | lowercase log level (info by default)             |
| RETURN_MOCK_DATA          | no        | boolean         | return fake facts                                 |
| prometheus_multiproc_dir  | yes       | string          | path to dir for sharing stats between processes   |
| PATH_PREFIX               | no        | string          | API path prefix (default: `/r/insights/platform`) |
| APP_NAME                  | no        | string          | API app name (default: `drift`)                   |

If you would like to use this service with insights-proxy, you can use the
included `local-drift-backend.js` like so:

`SPANDX_CONFIG=drift-backend/local-drift-backend.js bash insights-proxy/scripts/run.sh`


If you use `run_app.sh`, drift app will be invoked via gunicorn. This should be
OK in most cases; even `pdb` runs fine inside of gunicorn.

However, if you want to use flask's server, use `python3 standalone_flask_server.py`
with the aforementioned environment vars.
