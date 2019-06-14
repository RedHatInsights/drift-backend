#!/usr/bin/env python

import json

lockfile = {}

with open("Pipfile.lock") as json_file:
    lockfile = json.load(json_file)

dependencies = []
for name, value in lockfile["default"].items():
    version = value["version"].replace("=", "")
    dependencies.append("drift/python:3.6=%s:%s\n" % (name, version))

dependencies.sort()
with open("drift-manifest", "w") as manifest:
    for item in dependencies:
        manifest.write(item)
