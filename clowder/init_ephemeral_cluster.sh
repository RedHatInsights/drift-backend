#!/usr/bin/env

# See step 7 of this link: https://clouddot.pages.redhat.com/docs/dev/getting-started/ephemeral/onboarding.html
echo "Loggin to Openshift cluster"
sh ~/ephemeral-login.sh

echo "Reserving namespace for 2 hours"
export NAMESPACE=$(bonfire namespace reserve -d 2)

echo "Namespace $NAMESPACE reserved"

echo "Using $NAMESPACE as default oc project"
oc project $NAMESPACE

echo "Deploying apps to $NAMESPACE"
bonfire deploy drift xjoin-search -n $NAMESPACE

sh ./clowder/clowder-port-forward.sh