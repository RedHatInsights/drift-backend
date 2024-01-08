#!/bin/bash

# this script is a wrapper for nosetests. It ensures that
# 'prometheus_multiproc_dir' is set up and torn down.

TEMPDIR=`mktemp -d`

psql 'postgresql://insights:insights@localhost:5432' -c 'create database testdb;'

BASELINE_DB_NAME=testdb FLASK_APP=historical_system_profiles.app:get_flask_app_with_migration flask db upgrade

BASELINE_DB_NAME=testdb prometheus_multiproc_dir=$TEMPDIR pytest --cov-report xml ./tests "$@"  && rm -rf $TEMPDIR

result=$?

psql 'postgresql://insights:insights@localhost:5432' -c 'drop database testdb;'

exit $result
