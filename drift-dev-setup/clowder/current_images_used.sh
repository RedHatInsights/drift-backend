#!/usr/bin/env sh
oc describe deployments | grep '^[[:blank:]]*Image:' | awk '{print $2}' | sort | uniq
