#!/usr/bin/env

# See step 7 of this link: https://clouddot.pages.redhat.com/docs/dev/getting-started/ephemeral/onboarding.html
echo "Loggin to Openshift cluster"
sh ~/ephemeral-login.sh
echo "Checking for reserved namespace"
export NAMESPACE=$(bonfire namespace list --mine | grep "ephemeral" | awk '{print $1$2}' | xargs -n1)

if [[ $NAMESPACE == *"ephemeral-"*"true" ]]; then
    echo "Namespace $NAMESPACE reserved, extending for 2 hours"    
    bonfire namespace reserve -d 2 $NAMESPACE 
else
    echo "Reserving namespace for 2 hours"
    export NAMESPACE=$(bonfire namespace reserve -d 2)
    echo "Namespace $NAMESPACE reserved"
fi

echo "Using $NAMESPACE as default oc project"
oc project $NAMESPACE

echo "Deploying apps to $NAMESPACE"
bonfire deploy drift xjoin-search -n $NAMESPACE

sh ./clowder/clowder-port-forward.sh