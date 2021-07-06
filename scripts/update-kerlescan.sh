#!/usr/bin/sh

echo "Fetching kerlescan tags"
TAG=$(git ls-remote --sort='version:refname' --tags https://github.com/RedHatInsights/kerlescan.git | tail -n 1 | cut --delimiter='/' --fields=3)
echo "Latest kerlescan tag is $TAG"

echo "Installing kerlescan $TAG"
pipenv install -e git+https://github.com/RedHatInsights/kerlescan.git@$TAG#egg=kerlescan
echo "Kerlescan $TAG installed"

echo "Creating manifest"
pipenv run scripts/create-manifest.py
echo "Manifest created."
