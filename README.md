# drift-backend
System drift analysis service

this is a flask app that provides api for drift-frontend. It listens on port 8080 by default.

To run:

`INVENTORY_SVC_URL=<inventory service url> python3 app.py`


To set the debug level (`INFO` by default):

`LOG_LEVEL=DEBUG INVENTORY_SVC_URL=<inventory service url> python3 app.py`
