#!/usr/bin/env sh
PROBE_FILE="${READINESS_PROBE_FILE:-/tmp/readiness_probe}"

if [ -e "$PROBE_FILE" ]; then
    # file exists
    # echo 'new'
    exit 0
fi
# file doesn't exist
# echo 'no file'
exit 1
