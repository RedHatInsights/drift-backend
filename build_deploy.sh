#!/bin/bash

set -exv

IMAGE_NAME="quay.io/cloudservices/drift-backend"
IMAGE_TAG=$(git rev-parse --short=7 HEAD)
SECURITY_COMPLIANCE_TAG="sc-$(date +%Y%m%d)-$(git rev-parse --short=7 HEAD)"

if [[ -z "$QUAY_USER" || -z "$QUAY_TOKEN" ]]; then
    echo "QUAY_USER and QUAY_TOKEN must be set"
    exit 1
fi

# Create tmp dir to store data in during job run (do NOT store in $WORKSPACE)
export TMP_JOB_DIR=$(mktemp -d -p "$HOME" -t "jenkins-${JOB_NAME}-${BUILD_NUMBER}-XXXXXX")
echo "job tmp dir location: $TMP_JOB_DIR"

if [[ "$GIT_BRANCH" == "origin/security-compliance" ]]; then
    PUSH_TAG="${SECURITY_COMPLIANCE_TAG}"
else
    PUSH_TAG=("latest" "qa")
fi

if test -f /etc/redhat-release && grep -q -i "release 7" /etc/redhat-release; then

function job_cleanup() {
    echo "cleaning up job tmp dir: $TMP_JOB_DIR"
    rm -fr $TMP_JOB_DIR
}

trap job_cleanup EXIT ERR SIGINT SIGTERM
    
# on RHEL7, use docker

AUTH_CONF_DIR="${TMP_JOB_DIR}/.docker"
mkdir -p $AUTH_CONF_DIR

    docker --config="$DOCKER_CONF" login -u="$QUAY_USER" -p="$QUAY_TOKEN" quay.io
    docker --config="$DOCKER_CONF" login -u="$RH_REGISTRY_USER" -p="$RH_REGISTRY_TOKEN" registry.redhat.io
    docker --config="$DOCKER_CONF" build -t "${IMAGE_NAME}:${IMAGE_TAG}" .
    docker --config="$DOCKER_CONF" push "${IMAGE_NAME}:${IMAGE_TAG}"

    for TAG in "${PUSH_TAG[@]}"; do
        docker --config="$DOCKER_CONF" tag "${IMAGE_NAME}:${IMAGE_TAG}" "${IMAGE_NAME}:$TAG"
        docker --config="$DOCKER_CONF" push "${IMAGE_NAME}:$TAG"
    done

else
    # on RHEL8 or anything else, use podman
    AUTH_CONF_DIR="${TMP_JOB_DIR}/.podman"
    mkdir -p $AUTH_CONF_DIR
    export REGISTRY_AUTH_FILE="$AUTH_CONF_DIR/auth.json"
    podman login -u="$QUAY_USER" -p="$QUAY_TOKEN" quay.io
    podman login -u="$RH_REGISTRY_USER" -p="$RH_REGISTRY_TOKEN" registry.redhat.io
    podman build -t "${IMAGE_NAME}:${IMAGE_TAG}" .
    podman push "${IMAGE_NAME}:${IMAGE_TAG}"

    for TAG in "${PUSH_TAG[@]}"; do
        podman tag "${IMAGE_NAME}:${IMAGE_TAG}" "${IMAGE_NAME}:$TAG"
        podman push "${IMAGE_NAME}:$TAG"
    done
fi
