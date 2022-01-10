#!/usr/bin/env

# See step 7 of this link: https://clouddot.pages.redhat.com/docs/dev/getting-started/ephemeral/onboarding.html
echo "Logging into Openshift cluster"
sh ~/ephemeral-login.sh
echo "Checking for reserved namespace"
export NAMESPACE=$(bonfire namespace list --mine | grep "ephemeral" | awk '{print $1"|"$2}' | grep '|true' | awk -F'|' '{print $1}' | head -n1) # we use the first one available

if [[ $NAMESPACE == *"ephemeral-"* ]]; then
    echo "Namespace $NAMESPACE reserved, extending for 2 hours"    
    bonfire namespace extend $NAMESPACE -d '2h0m' 
else
    echo "Reserving namespace for 2 hours"
    export NAMESPACE=$(bonfire namespace reserve -d '2h0m')
    echo "Namespace $NAMESPACE reserved"
fi

echo "Using $NAMESPACE as default oc project"
oc project $NAMESPACE

echo "Deploying apps to $NAMESPACE"
bonfire deploy drift -n $NAMESPACE

sh ./clowder/clowder-port-forward.sh
