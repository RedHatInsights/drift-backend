#!/usr/bin/env sh

export NOTIFICATIONS_BACKEND__REF="master"
export NOTIFICATIONS_GW__REF="main"

CLOWDER_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

echo $CLOWDER_DIR
envsubst < $CLOWDER_DIR/pr_check_bonfire_config_template.yaml > $CLOWDER_DIR/pr_check_bonfire_config.yaml
