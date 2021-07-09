#!/bin/bash

# this script is a wrapper for nosetests. It ensures that
# 'prometheus_multiproc_dir' is set up and torn down.

TEMPDIR=`mktemp -d`

prometheus_multiproc_dir=$TEMPDIR pytest ./tests --cov-report term-missing --cov=. --cov-fail-under=73  --no-cov-on-fail "$@" && prometheus_multiproc_dir=$TEMPDIR python generate_report.py test_reports.toml && rm -rf $TEMPDIR
