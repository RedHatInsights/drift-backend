# drift-backend
System drift analysis service

This is a flask app that provides api for drift-frontend. It listens on port
8080 by default.

To run:

`INVENTORY_SVC_URL=<inventory service url> python3 app.py`


To set the debug level (`INFO` by default):

`LOG_LEVEL=DEBUG INVENTORY_SVC_URL=<inventory service url> python3 app.py`

If you would like to use this service with insights-proxy, you can use the
included `local-drift-backend.js` like so, from the `insights-chrome/build`
dir:

`SPANDX_CONFIG=/path/to/drift-backend/local-drift-backend.js bash ../../insights-proxy/scripts/run.sh`
