#!/bin/bash

# this script is a wrapper for nosetests. It ensures that
# 'prometheus_multiproc_dir' is set up and torn down.

TEMPDIR=`mktemp -d`

prometheus_multiproc_dir=$TEMPDIR nosetests -sx --with-coverage --cover-package drift  --cover-min-percentage 78 --cover-erase && prometheus_multiproc_dir=$TEMPDIR python generate_report.py test_reports.toml && rm -rf $TEMPDIR
