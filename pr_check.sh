#!/bin/bash

#fetch our shared bonfire config
curl -o config.yaml https://raw.githubusercontent.com/RedHatInsights/drift-dev-setup/master/clowder/pr_check_bonfire_config.yaml

#Adapted from https://github.com/RedHatInsights/insights-ingress-go/blob/master/pr_check.sh

# --------------------------------------------
# Options that must be configured by app owner
# --------------------------------------------
APP_NAME="drift"  # name of app-sre "application" folder this component lives in
COMPONENT_NAME="system-baseline"  # name of app-sre "resourceTemplate" in deploy.yaml for this component
IMAGE="quay.io/cloudservices/system-baseline-backend"

IQE_PLUGINS="drift"
IQE_MARKER_EXPRESSION="smoke" # Need to check this
IQE_FILTER_EXPRESSION=""
IQE_CJI_TIMEOUT="30m"


# Install bonfire repo/initialize
CICD_URL=https://raw.githubusercontent.com/RedHatInsights/bonfire/master/cicd
curl -s $CICD_URL/bootstrap.sh > .cicd_bootstrap.sh && source .cicd_bootstrap.sh
source $CICD_ROOT/build.sh
# source $APP_ROOT/ephemeral_unit_test.sh
source $APP_ROOT/baseline_deploy_ephemeral_env.sh
source $CICD_ROOT/cji_smoke_test.sh
