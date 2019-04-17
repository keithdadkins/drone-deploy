#!/usr/bin/env bash
# Builds an aws-cli docker image that we can use during builds
AWS_CLI_BASE_IMAGE="${AWS_CLI_BASE_IMAGE:-}"

# build image
sudo docker build -f aws-cli.Dockerfile -t aws-cli --build-arg CLI_BASE_IMAGE="${AWS_CLI_BASE_IMAGE}" .

# test aws-cli
if sudo docker run --rm aws-cli -- aws sts get-caller-identity > /dev/null 2>&1; then
    echo "Successfully built aws-cli.Dockerfile"
else
    echo "Error building aws-cli.Dockerfile"
    exit1
fi
