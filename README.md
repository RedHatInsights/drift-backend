# drift-backend
host drift analysis service

this is a flask app that provides api for drift-frontend. It listens on port 8080 by default.

To run:

`python3 app.py`


To enable debug mode (DO NOT USE THIS IN PRODUCTION, stack traces will be shown to the user when uncaught exceptions are raised):

`DRIFT_DEBUG=1 python3 app.py`

We recommend simply not defining `DRIFT_DEBUG` if you don't want debug mode enabled.
