#!/usr/bin/env bash

# VALIDATES IF WE HAVE CLOWDER ENV
TEMPDIR=`mktemp -d`
export ACG_CONFIG="./local_cdappconfig.json"
if [ -z "$ACG_CONFIG" ]; then
  echo "Did not found ACG_CONFIG - RUNNING LOCALLY"

  if [ -z "$INVENTORY_SVC_URL" ];
    then echo "INVENTORY_SVC_URL is not set" && exit 1;
  fi

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
  export prometheus_multiproc_dir=$TEMPDIR
  PORT=8001
  METRICS_PORT=9001
  APP_CONFIG='gunicorn.conf.py'
  exec gunicorn wsgi --bind=0.0.0.0:$PORT --bind=0.0.0.0:$METRICS_PORT --access-logfile=- --config "$APP_CONFIG"
fi
rm -rf $TEMPDIR
