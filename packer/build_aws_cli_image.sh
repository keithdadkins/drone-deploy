#!/usr/bin/env bash
# Builds an aws-cli docker image that we can use during builds

# build image
sudo docker build -f aws-cli.Dockerfile -t aws-cli .

# test aws-cli
ver="$(sudo docker run --rm -e ${AWS_ACCESS_KEY_ID} -e ${AWS_SECRET_ACCESS_KEY} aws-cli sts get-caller-identity > /dev/null 2>&1)"
[ $? -eq 0 ] && echo "aws-cli docker file tested successfully" || exit 1
