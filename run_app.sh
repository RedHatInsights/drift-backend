TEMPDIR=`mktemp -d`

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

prometheus_multiproc_dir=$TEMPDIR gunicorn wsgi -w $NUM_WORKERS --threads $THREADS -b 0.0.0.0:8080 --log-level=$LOG_LEVEL --access-logfile=- --config ./gunicorn.conf.py

rm -rf $TEMPDIR
