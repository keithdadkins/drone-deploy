#!/usr/bin/env bash
# Builds an aws-cli docker image that we can use during builds
AWS_CLI_BASE_IMAGE="${AWS_CLI_BASE_IMAGE:-}"
# AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID:-}"
# AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY:-}"

# # fail if credentials are not set
# if [ -z "${AWS_ACCESS_KEY_ID-x}" ] || [ -z "${AWS_SECRET_ACCESS_KEY-x}" ]; then
#     echo "AWS access key and secret must be set.. exiting."
#     exit 1
# fi

# failed_test(){
#     echo "aws-cli was unable to connect to aws successfully."
#     echo "When running 'aws sts get-caller-identity', the response given was: "
#     result=$(sudo docker run --rm -e AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID}" -e AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY}" aws-cli -- aws sts get-caller-identity)
#     echo "$result"
#     echo "Exiting."
#     exit 1
# }

# build image
sudo docker build -f aws-cli.Dockerfile -t aws-cli --build-arg CLI_BASE_IMAGE="${AWS_CLI_BASE_IMAGE}" .

# test aws-cli
sudo docker run --rm aws-cli -- aws sts get-caller-identity > /dev/null 2>&1
[ $? -eq 0 ] && echo "aws-cli docker file tested successfully" || failed_test
