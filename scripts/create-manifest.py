#!/usr/bin/env python

import json

lockfile = {}

with open("Pipfile.lock") as json_file:
    lockfile = json.load(json_file)

with open("system_baseline-manifest", "w") as manifest:
    for name, value in lockfile["default"].items():
        if "version" in value:
            version = value["version"].replace("=", "")
            manifest.write("system_baseline/python:3.6=%s:%s\n" % (name, version))
        elif "ref" in value:
            ref = value["ref"]
            manifest.write("system_baseline/python:3.6=%s:%s\n" % (name, ref))
        else:
            raise "unable to parse %s" % value
