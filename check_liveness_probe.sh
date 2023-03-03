#!/usr/bin/env sh
PROBE_FILE="${LIVENESS_PROBE_FILE:-/tmp/liveness_probe}"

if [ -e "$PROBE_FILE" ]; then
    if [ "$(find \""$PROBE_FILE\"" -mmin +1)" ]; then
        # file exists and is older than 1 minute
        # echo 'old'
        exit 1
    fi
    # file exists and is new
    # echo 'new'
    exit 0
fi
# file doesn't exist
# echo 'no file'
exit 1
