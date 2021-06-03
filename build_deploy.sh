#!/bin/bash

set -exv

IMAGE_NAME="quay.io/cloudservices/drift-backend"
IMAGE_TAG=$(git rev-parse --short=7 HEAD)

if [[ -z "$QUAY_USER" || -z "$QUAY_TOKEN" ]]; then
    echo "QUAY_USER and QUAY_TOKEN must be set"
    exit 1
fi

DOCKER_CONF="$PWD/.docker"
mkdir -p "$DOCKER_CONF"

docker --config="$DOCKER_CONF" login -u="$QUAY_USER" -p="$QUAY_TOKEN" quay.io
docker --config="$DOCKER_CONF" login -u="$RH_REGISTRY_USER" -p="$RH_REGISTRY_TOKEN" registry.redhat.io
docker --config="$DOCKER_CONF" build -t "${IMAGE_NAME}:${IMAGE_TAG}" .
docker --config="$DOCKER_CONF" push "${IMAGE_NAME}:${IMAGE_TAG}"

# To enable backwards compatibility with ci, qa, and smoke, always push latest and qa tags

for TAG in "latest" "qa-new"; do
    docker --config="$DOCKER_CONF" tag "${IMAGE_NAME}:${IMAGE_TAG}" "${IMAGE_NAME}:$TAG"
    docker --config="$DOCKER_CONF" push "${IMAGE_NAME}:$TAG"
done
