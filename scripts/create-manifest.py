#!/usr/bin/env python

import json
import os

modified_time = int(os.path.getmtime("Pipfile.lock"))
lockfile = {}

with open("Pipfile.lock") as json_file:
    lockfile = json.load(json_file)

with open("drift-manifest", "w") as manifest:
    for name, value in sorted(lockfile["default"].items()):
        if "version" in value:
            version = value["version"].replace("=", "")
            manifest.write("services-drift:drift/python:3.8=%s:%s\n" % (name, version))
        elif "ref" in value:
            ref = value["ref"]
            manifest.write("services-drift:drift/python:3.8=%s:%s\n" % (name, ref))
        else:
            raise f"unable to parse {value}"
