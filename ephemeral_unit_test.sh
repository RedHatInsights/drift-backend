#!/bin/bash

cd $APP_ROOT

source $APP_ROOT/baseline_deploy_ephemeral_db.sh

# Get DB env variables from bonfire `deploy_ephemeral_db.sh`
export BASELINE_DB_NAME=$DATABASE_NAME
export BASELINE_DB_HOST=$DATABASE_HOST
export BASELINE_DB_PORT=$DATABASE_PORT
export BASELINE_DB_USER=$DATABASE_USER
export BASELINE_DB_PASS=$DATABASE_PASSWORD
export PGPASSWORD=$DATABASE_ADMIN_PASSWORD

#Start Python venv
python3.8 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel pipenv
pipenv install --dev

#Run unit test
TEMPDIR=`mktemp -d`

FLASK_APP=system_baseline.app:get_flask_app_with_migration flask db upgrade

prometheus_multiproc_dir=$TEMPDIR pytest . "$@" --junitxml=junit-unittest.xml && rm -rf $TEMPDIR

result=$?

deactivate

source .bonfire_venv/bin/activate

bonfire namespace release $NAMESPACE

mkdir -p $WORKSPACE/artifacts
cp junit-unittest.xml ${WORKSPACE}/artifacts/junit-unittest.xml

cd -
