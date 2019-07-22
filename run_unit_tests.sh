#!/bin/bash

# this script is a wrapper for nosetests. It ensures that
# 'prometheus_multiproc_dir' is set up and torn down.

TEMPDIR=`mktemp -d`

psql 'postgresql://insights:insights@localhost:5432' -c 'create database testdb;'

BASELINE_DB_NAME=testdb FLASK_APP=system_baseline.app:get_flask_app_with_migration flask db upgrade

BASELINE_DB_NAME=testdb prometheus_multiproc_dir=$TEMPDIR nosetests --with-coverage --cover-package system_baseline  --cover-min-percentage 75 --cover-erase && rm -rf $TEMPDIR

psql 'postgresql://insights:insights@localhost:5432' -c 'drop database testdb;'
