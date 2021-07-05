#!/usr/bin/env python

import json


lockfile = {}

with open("Pipfile.lock") as json_file:
    lockfile = json.load(json_file)

with open("historical_system_profiles-manifest", "w") as manifest:
    for name, value in sorted(lockfile["default"].items()):
        if "version" in value:
            version = value["version"].replace("=", "")
            manifest.write(
                "services-drift:historical_system_profiles/python:3.8=%s:%s\n" % (name, version)
            )
        elif "ref" in value:
            ref = value["ref"]
            manifest.write(
                "services-drift:historical_system_profiles/python:3.8=%s:%s\n" % (name, ref)
            )
        else:
            raise "unable to parse %s" % value
