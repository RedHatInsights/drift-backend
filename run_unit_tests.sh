#!/bin/bash

# this script is a wrapper for nosetests. It ensures that
# 'prometheus_multiproc_dir' is set up and torn down.

TEMPDIR=`mktemp -d`
export UNLEASH_TOKEN="token"

prometheus_multiproc_dir=$TEMPDIR pytest "$@" && prometheus_multiproc_dir=$TEMPDIR python generate_report.py test_reports.toml && rm -rf $TEMPDIR
