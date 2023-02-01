#!/usr/bin/env bash

if [ "$ACG_CONFIG" ]
then
  echo "Found ACG_CONFIG - RUNNING WITH CLOWDER"

  if [ -z "$SERVICE_MODE" ];
    then SERVICE_MODE=REST_API
  fi
  if [ "$SERVICE_MODE" == "REST_API" ]
  then
    echo "RUNNING BACKEND SERVICE"
    PORT=8000
    METRICS_PORT=9000
    GUNICORN_REQUEST_FIELD_LIMIT=16380
    APP_CONFIG='gunicorn.conf.py'
    FLASK_APP=historical_system_profiles.app:get_flask_app_with_migration flask db upgrade;
    if [[ "$?" != "0" ]]; then exit 1; fi
    exec gunicorn wsgi --bind=0.0.0.0:$PORT --bind=0.0.0.0:$METRICS_PORT --limit-request-field_size=$GUNICORN_REQUEST_FIELD_LIMIT --access-logfile=- --config "$APP_CONFIG"
  elif [ "$SERVICE_MODE" == "CLEAN_EXPIRED_RECORDS" ];
    then
    echo "RUNNING CLEAN_EXPIRED_RECORDS"
    python clean_expired_records.py
  elif [ "$LISTENER_TYPE" == "ARCHIVER" ];
    then
    echo "RUNNING ARCHIVER"
    python kafka_listener.py
  elif [ "$LISTENER_TYPE" == "DELETER" ];
    then
    echo "RUNNING DELETER"
    python kafka_listener.py
  fi

else
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

  if [ -z "$SERVICE_MODE" ];
    then SERVICE_MODE=REST_API
  fi

  if [ -z "$GUNICORN_REQUEST_FIELD_LIMIT" ];
    then GUNICORN_REQUEST_FIELD_LIMIT=16380
  fi

  if [ "$SERVICE_MODE" == "REST_API" ];
  then prometheus_multiproc_dir=$TEMPDIR gunicorn wsgi -w $NUM_WORKERS --threads $THREADS -b 0.0.0.0:$PORT --log-level=$LOG_LEVEL --limit-request-field_size=$GUNICORN_REQUEST_FIELD_LIMIT --access-logfile=- --config ./gunicorn.conf.py
  elif [ "$SERVICE_MODE" == "CLEAN_EXPIRED_RECORDS" ];
    then prometheus_multiproc_dir=$TEMPDIR python clean_expired_records.py
  elif [ "$LISTENER_TYPE" == "ARCHIVER" ];
    then python kafka_listener.py
  elif [ "$LISTENER_TYPE" == "DELETER" ];
    then python kafka_listener.py
  fi

  rm -rf $TEMPDIR

fi
