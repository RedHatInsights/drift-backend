#!/usr/bin/env bash

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
