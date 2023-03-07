#!/bin/bash

./scripts/create-manifest.py

changed=`git diff --name-only HEAD`

if [[ $changed == *"drift-manifest"* ]]; then
  echo "Pipfile.lock or poetry.lock changed without updating drift-manifest since latest commit. Run ./scripts/create-manifest.py to update drift-manifest, then commit."
  exit 1
else
  exit 0
fi
