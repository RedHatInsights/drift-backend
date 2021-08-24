#!/bin/bash

set -exv

IMAGE_NAME="quay.io/cloudservices/drift-backend"
IMAGE_TAG=$(git rev-parse --short=7 HEAD)

if [[ -z "$QUAY_USER" || -z "$QUAY_TOKEN" ]]; then
    echo "QUAY_USER and QUAY_TOKEN must be set"
    exit 1
fi

if test -f /etc/redhat-release && grep -q -i "release 7" /etc/redhat-release; then
    # on RHEL7, use docker
    DOCKER_CONF="$PWD/.docker"
    mkdir -p "$DOCKER_CONF"
    docker --config="$DOCKER_CONF" login -u="$QUAY_USER" -p="$QUAY_TOKEN" quay.io
    docker --config="$DOCKER_CONF" login -u="$RH_REGISTRY_USER" -p="$RH_REGISTRY_TOKEN" registry.redhat.io
    docker --config="$DOCKER_CONF" build -t "${IMAGE_NAME}:${IMAGE_TAG}" .
    docker --config="$DOCKER_CONF" push "${IMAGE_NAME}:${IMAGE_TAG}"
    for TAG in "latest" "qa"; do
        docker --config="$DOCKER_CONF" tag "${IMAGE_NAME}:${IMAGE_TAG}" "${IMAGE_NAME}:$TAG"
        docker --config="$DOCKER_CONF" push "${IMAGE_NAME}:$TAG"
    done
else
    # on RHEL8 or anything else, use podman
    AUTH_CONF_DIR="$(pwd)/.podman"
    mkdir -p $AUTH_CONF_DIR
    export REGISTRY_AUTH_FILE="$AUTH_CONF_DIR/auth.json"
    podman login -u="$QUAY_USER" -p="$QUAY_TOKEN" quay.io
    podman login -u="$RH_REGISTRY_USER" -p="$RH_REGISTRY_TOKEN" registry.redhat.io
    podman build -t "${IMAGE}:${IMAGE_TAG}" .
    podman push "${IMAGE}:${IMAGE_TAG}"
    for TAG in "latest" "qa"; do
        podman tag "${IMAGE_NAME}:${IMAGE_TAG}" "${IMAGE_NAME}:$TAG"
        podman push "${IMAGE_NAME}:$TAG"
    done
fi
