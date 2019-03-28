#!/bin/bash

# this script is a wrapper for nosetests. It ensures that
# 'prometheus_multiproc_dir' is set up and torn down.

TEMPDIR=`mktemp -d`

prometheus_multiproc_dir=$TEMPDIR nosetests --with-coverage --cover-package drift  --cover-min-percentage 95 --cover-erase && rm -rf $TEMPDIR
