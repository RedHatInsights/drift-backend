#!/bin/bash

./scripts/create-manifest.py

changed=`git diff --name-only HEAD`

if [[ $changed == *"historical_system_profiles-manifest"* ]]; then
  echo "Pipfile.lock changed without updating historical_system_profiles-manifest. Run ./scripts/create-manifest.py to update."
  exit 1
else
  exit 0
fi
