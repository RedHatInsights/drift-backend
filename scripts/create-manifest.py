#!/bin/env python

import json

lockfile = {}

with open("Pipfile.lock") as json_file:
    lockfile = json.load(json_file)

with open("system_baseline-manifest", "w") as manifest:
    for name, value in lockfile["default"].items():
        version = value["version"].replace("=", "")
        manifest.write("system_baseline/python:3.6=%s:%s\n" % (name, version))
