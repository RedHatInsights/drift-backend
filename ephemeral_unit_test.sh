#!/bin/bash

cd $APP_ROOT

#Start Python venv
python3.8 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel pipenv
pipenv install --dev

#Run unit test
TEMPDIR=`mktemp -d`

prometheus_multiproc_dir=$TEMPDIR pytest --cov=. tests/ "$@" --junitxml=junit-unittest.xml && prometheus_multiproc_dir=$TEMPDIR python generate_report.py test_reports.toml && rm -rf $TEMPDIR

result=$?

deactivate

mkdir -p $WORKSPACE/artifacts
cp junit-unittest.xml ${WORKSPACE}/artifacts/junit-unittest.xml

cd -
