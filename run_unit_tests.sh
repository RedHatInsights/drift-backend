#!/bin/bash

# this script is a wrapper for nosetests. It ensures that
# 'prometheus_multiproc_dir' is set up and torn down.

TEMPDIR=`mktemp -d`

prometheus_multiproc_dir=$TEMPDIR nosetests -sx --with-coverage --cover-package drift  --cover-min-percentage 80 --cover-erase && rm -rf $TEMPDIR
