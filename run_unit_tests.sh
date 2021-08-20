#!/bin/bash

# this script is a wrapper for nosetests. It ensures that
# 'prometheus_multiproc_dir' is set up and torn down.

TEMPDIR=`mktemp -d`

psql 'postgresql://insights:insights@localhost:5432/baselinedb' -c 'create database testdb;'

BASELINE_DB_NAME=testdb FLASK_APP=system_baseline.app:get_flask_app_with_migration flask db upgrade

BASELINE_DB_NAME=testdb prometheus_multiproc_dir=$TEMPDIR pytest . "$@"  && rm -rf $TEMPDIR

result=$?

psql 'postgresql://insights:insights@localhost:5432/baselinedb' -c 'drop database testdb;'

exit $result
