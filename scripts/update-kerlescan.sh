#!/usr/bin/sh

echo "Fetching kerlescan tags"
TAG=$(git ls-remote --sort='version:refname' --tags https://github.com/RedHatInsights/kerlescan.git | tail -n 1 | cut --delimiter='/' --fields=3)
echo "Latest kerlescan tag is $TAG"

echo "Installing kerlescan $TAG"
poetry add git+https://github.com/RedHatInsights/kerlescan.git#$TAG --editable
poetry lock --no-update
echo "Kerlescan $TAG installed"

echo "Creating manifest"
poetry run scripts/create-manifest.py
echo "Manifest created."
