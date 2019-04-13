#!/usr/bin/env bash
# Builds an aws-cli docker image that we can use during builds
AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID:-0}
AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY:-0}

# fail if credentials are not set
[ "${AWS_ACCESS_KEY_ID}" -eq "0" ] && echo "no AWS_ACCESS_KEY_ID found.. exiting." && exit 1
[ "${AWS_SECRET_ACCESS_KEY}" -eq "0" ] && echo "no AWS_SECRET_ACCESS_KEY found.. exiting." && exit 1

failed_test(){
    echo "aws-cli was unable to connect to aws successfully."
    echo "When running 'aws sts get-caller-identity', the response given was: "
    result=$(sudo docker run --rm -e AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID}" -e AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY}" aws-cli sts get-caller-identity)
    echo $result
    echo "Exiting."
    exit 1
}

# build image
sudo docker build -f aws-cli.Dockerfile -t aws-cli .

# test aws-cli
sudo docker run --rm -e AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID}" -e AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY}" aws-cli sts get-caller-identity > /dev/null 2>&1
[ $? -eq 0 ] && echo "aws-cli docker file tested successfully" || failed_test
