#!/usr/bin/env bash
# Builds an aws-cli docker image that we can use during builds

failed_test(){
    echo "aws-cli was unable to connect to aws successfully... "
    echo "$1"
    echo "Exiting."
    exit 1
}

# build image
sudo docker build -f aws-cli.Dockerfile -t aws-cli .

# test aws-cli
ver="$(sudo docker run --rm -e ${AWS_ACCESS_KEY_ID} -e ${AWS_SECRET_ACCESS_KEY} aws-cli sts get-caller-identity > /dev/null 2>&1)"
[ $? -eq 0 ] && echo "aws-cli docker file tested successfully" || failed_test $ver
