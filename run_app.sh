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

if [ "$SERVICE_MODE" == "REST_API" ];
  then prometheus_multiproc_dir=$TEMPDIR gunicorn wsgi -w $NUM_WORKERS --threads $THREADS -b 0.0.0.0:$PORT --log-level=$LOG_LEVEL --access-logfile=- --config ./gunicorn.conf.py
elif [ "$SERVICE_MODE" == "CLEAN_EXPIRED_RECORDS" ];
  then prometheus_multiproc_dir=$TEMPDIR python clean_expired_records.py
elif [ "$LISTENER_TYPE" == "ARCHIVER" ];
  then python kafka_listener.py
elif [ "$LISTENER_TYPE" == "DELETER" ];
  then python kafka_listener.py
fi

rm -rf $TEMPDIR
