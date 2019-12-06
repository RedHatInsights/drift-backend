#!/bin/bash

# this script is a wrapper for nosetests. It ensures that
# 'prometheus_multiproc_dir' is set up and torn down.

TEMPDIR=`mktemp -d`

prometheus_multiproc_dir=$TEMPDIR nosetests -sx --with-coverage --cover-package historical_system_profiles  --cover-min-percentage 90 --cover-erase && rm -rf $TEMPDIR

result=$?

exit $result
