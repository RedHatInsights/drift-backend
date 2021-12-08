#!/usr/bin/env bash

COMPONENT="system-baseline"
echo "Getting DB credentials from ephemeral cluster"
DB_CREDS=$(oc get secret ${COMPONENT} -o json | jq -r '.data["cdappconfig.json"]' | base64 -d | jq -r .database)
DB_USERNAME=$(jq .username <<< $DB_CREDS)
DB_PASSWORD=$(jq .password <<< $DB_CREDS)
DB_ADM_USERNAME=$(jq .adminUsername <<< $DB_CREDS)
DB_ADM_PASSWORD=$(jq .adminPassword <<< $DB_CREDS)
cat <<< $(jq '.database.username = '$DB_USERNAME' | .database.password = '$DB_PASSWORD'' ./local_cdappconfig.json) > ./local_cdappconfig.json
cat <<< $(jq '.database.adminPassword = '$DB_ADM_USERNAME' | .database.password = '$DB_ADM_PASSWORD'' ./local_cdappconfig.json) > ./local_cdappconfig.json
TEMPDIR=`mktemp -d`
export ACG_CONFIG="./local_cdappconfig.json"
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

  prometheus_multiproc_dir=$TEMPDIR gunicorn wsgi -w $NUM_WORKERS --threads $THREADS -b 0.0.0.0:$PORT --log-level=$LOG_LEVEL --access-logfile=- --config ./gunicorn.conf.py

  rm -rf $TEMPDIR
else
  echo "Found ACG_CONFIG - RUNNING WITH CLOWDER"
  echo "RUNNING SYSTEM BASELINE SERVICE"
  export prometheus_multiproc_dir=$TEMPDIR
  export LOG_LEVEL='debug'
  PORT=8003
  METRICS_PORT=9003
  APP_CONFIG='gunicorn.conf.py'
  FLASK_APP=system_baseline.app:get_flask_app_with_migration flask db upgrade;
  if [[ "$?" != "0" ]]; then exit 1; fi
  exec gunicorn wsgi --reload --bind=0.0.0.0:"$PORT" --bind=0.0.0.0:"$METRICS_PORT" --log-level="$LOG_LEVEL" --access-logfile=- --config "$APP_CONFIG"
fi
rm -rf $TEMPDIR
