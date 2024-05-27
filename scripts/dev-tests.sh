#!/usr/bin/env sh

# remove venv
poetry env remove --all

# install runtime and dev dependencies as defined in lockfile
poetry install --with dev --sync

# generate manifest file
poetry run ./scripts/create-manifest.py

# run unit tests
poetry run ./run_unit_tests.sh
