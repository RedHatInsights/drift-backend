#!/bin/bash

# this script is a wrapper for nosetests. It ensures that
# 'prometheus_multiproc_dir' is set up and torn down.

TEMPDIR=`mktemp -d`

# prefer nosetests-3, but use nosetests as fallback
command -v nosetests-3 >/dev/null 2>&1
retVal=$?

if [ $retVal -eq 0 ]; then
  NOSEBIN='nosetests-3'
else
  NOSEBIN='nosetests'
fi

prometheus_multiproc_dir=$TEMPDIR $NOSEBIN --with-coverage --cover-package drift  --cover-min-percentage 95 --cover-erase

rm -rf $TEMPDIR
