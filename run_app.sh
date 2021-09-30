#!/usr/bin/env bash

if [ -z "$ACG_CONFIG"]; then
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

  prometheus_multiproc_dir=$TEMPDIR gunicorn wsgi -w $NUM_WORKERS --threads $THREADS -b 0.0.0.0:$PORT --log-level=$LOG_LEVEL --access-logfile=- --config ./gunicorn.conf.py

  rm -rf $TEMPDIR
else
  echo "Found ACG_CONFIG - RUNNING WITH CLOWDER"
  echo "RUNNING SYSTEM BASELINE SERVICE"
  PORT=8000
  APP_CONFIG='gunicorn.conf.py'
  bash -c "FLASK_APP=system_baseline.app:get_flask_app_with_migration flask db upgrade"
  exec gunicorn wsgi --bind=0.0.0.0:$PORT --access-logfile=- --config "$APP_CONFIG"
fi
