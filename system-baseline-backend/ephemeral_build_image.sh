#!/usr/bin/env sh
# This script build and push an image to a quay.io repository

if [ $1 ]; then
    echo "Building image and pushing to quay.io/$1/system-baseline-backend"
    echo "Image expires in 2 days"
    IMAGE_TAG=$(git rev-parse --short=7 HEAD)
    echo "Using IMAGE_TAG: $IMAGE_TAG"
    docker build --label quay.expires-after=2d . --tag quay.io/$1/system-baseline-backend:$IMAGE_TAG
    docker push quay.io/$1/system-baseline-backend:$IMAGE_TAG
else
    echo 'Please provide your quay.io username'
fi
