# drift-backend
System drift analysis service

This is a flask app that provides api for drift-frontend. It listens on port
8080 by default.

To run:

`INVENTORY_SVC_URL=<inventory service url> python3 app.py`


To set the debug level (`INFO` by default):

`LOG_LEVEL=DEBUG INVENTORY_SVC_URL=<inventory service url> python3 app.py`

You may also set `RETURN_MOCK_DATA` to `true` if you want a large set of mock
facts returned for each system.

The same info as above, but in handy table form:

| env var name      | required? | expected values | description                                     |
| ------------      | --------- | --------------- | ------------                                    |
| INVENTORY_SVC_URL | yes       | URL             | URL for inventory service (do not include path) |
| LOG_LEVEL         | no        | boolean         | log level (INFO by default)                     |
| RETURN_MOCK_DATA  | no        | boolean         | return fake facts                               |

If you would like to use this service with insights-proxy, you can use the
included `local-drift-backend.js` like so:

`SPANDX_CONFIG=drift-backend/local-drift-backend.js bash insights-proxy/scripts/run.sh`
