#!/usr/bin/env bash
# Builds an aws-cli docker image that we can use during builds
AWS_CLI_BASE_IMAGE=${AWS_CLI_BASE_IMAGE:-}
DRONE_REGION=${DRONE_REGION:-}
set -euo pipefail

printf "\n\n\n\n***** BUILDING AWS-CLI *****\n\n\n\n"

# fail if env vars are not set
var_fail_message="must be set to build the aws-cli image... exiting."
[ -z "$AWS_CLI_BASE_IMAGE" ] && echo "AWS_CLI_BASE_IMAGE $var_fail_message" && exit 1
[ -z "$DRONE_REGION" ] && echo "DRONE_REGION $var_fail_message" && exit 1


# set our $aws command (just a shortcut instead of writing out a long docker run command everytime)
get_docker_cmd(){
    local docker_cmd='docker'
    [ "$EUID" -eq 0 ] && docker_cmd="sudo docker"
    echo "$docker_cmd"
}
docker="$(get_docker_cmd)"
aws="$docker run --rm aws-cli -- aws"


# build image
$docker build -f aws-cli.Dockerfile -t aws-cli --build-arg CLI_BASE_IMAGE="$AWS_CLI_BASE_IMAGE" .


# test
if $aws sts get-caller-identity > /dev/null 2>&1; then
    echo "Successfully built aws-cli.Dockerfile"
else
    echo "Error building aws-cli.Dockerfile"
    exit 1
fi


# create aws config for ubuntu user
mkdir -p /home/ubuntu/.aws

# write config to file
cat << EOF > /home/ubuntu/.aws/config
[default]
region=$DRONE_REGION
credential_source = Ec2InstanceMetadata
EOF

sudo chown -R ubuntu:ubuntu /home/ubuntu/.aws/config
