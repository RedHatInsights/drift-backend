#!/usr/bin/env bash

if [ -z "$ACG_CONFIG" ]; then
  echo "Did not found ACG_CONFIG - RUNNING LOCALLY"

  TEMPDIR=`mktemp -d`

  if [ -z "$LOG_LEVEL" ];
    then LOG_LEVEL='info'
  fi

  if [ -z "$NUM_WORKERS" ];
    then NUM_WORKERS=2
  fi

  if [ -z "$THREADS" ];
    then THREADS=2
  fi

  if [ -z "$PORT" ];
    then PORT=8080
  fi

  if [ -z "$GUNICORN_REQUEST_FIELD_LIMIT" ];
    then GUNICORN_REQUEST_FIELD_LIMIT=16380
  fi

  prometheus_multiproc_dir=$TEMPDIR gunicorn wsgi -w $NUM_WORKERS --threads $THREADS -b 0.0.0.0:$PORT --log-level=$LOG_LEVEL --access-logfile=- --limit-request-field_size=$GUNICORN_REQUEST_FIELD_LIMIT --config ./gunicorn.conf.py

  rm -rf $TEMPDIR
else
  echo "Found ACG_CONFIG - RUNNING WITH CLOWDER"
  echo "RUNNING SYSTEM BASELINE SERVICE"
  PORT=8000
  METRICS_PORT=9000
  GUNICORN_REQUEST_FIELD_LIMIT=16380
  APP_CONFIG='gunicorn.conf.py'
  FLASK_APP=system_baseline.app:get_flask_app_with_migration flask db upgrade;
  if [[ "$?" != "0" ]]; then exit 1; fi
  exec gunicorn wsgi --bind=0.0.0.0:$PORT --bind=0.0.0.0:$METRICS_PORT --access-logfile=- --limit-request-field_size=$GUNICORN_REQUEST_FIELD_LIMIT --config "$APP_CONFIG"
fi
