#!/usr/bin/env sh
PROBE_FILE="${LIVENESS_PROBE_FILE:-liveness_probe}"
PROBE_STALE_MINUTES=$((3*"${EXPIRED_CLEANER_SLEEP_MINUTES:-20}"))

if [ -e "$PROBE_FILE" ]; then
    if [ "$(find \""$PROBE_FILE\"" -mmin +\""$PROBE_STALE_MINUTES\"")" ]; then
        # file exists and is older than 3x expired cycle minutes
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

