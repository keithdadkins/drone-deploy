#!/usr/bin/env bash
# boostraps an initial drone server. drone will subsequently 
# be used to build and deploy updates after that.
set -x
AWS_CLI_BASE_IMAGE=${AWS_CLI_BASE_IMAGE:-python:3.7}
AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID:-}
AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY:-}
AWS_REGION=${AWS_REGION:-us-east-1}
AWS_DEFAULT_PROFILE=${AWS_DEFAULT_PROFILE:-}

# check for for docker (use sudo if script was run as root)
docker_cmd=
if [ "$EUID" -eq 0 ]; then
    sudo docker images > /dev/null 2>&1 && docker_cmd='sudo docker'
else
    docker images > /dev/null 2>&1 && docker_cmd='docker'
fi
[ -z "${docker_cmd+x}" ] && echo "Can't connect to docker. Is it running?" && exit 1

# build aws-cli image
echo "Building aws-cli image."
$docker_cmd build -f packer/aws-cli.Dockerfile -t aws-cli --build-arg CLI_BASE_IMAGE=${AWS_CLI_BASE_IMAGE} .
[ $? -ne 0 ] && echo "Error building the aws-cli image... exiting." && exit 1

# are aws access keys being used?
if [ -z "${AWS_ACCESS_KEY_ID-x}" ] && [ -z "${AWS_SECRET_ACCESS_KEY-x}"]; then
    # access keys are not being used.. mount local aws config and use profile instead
    docker_test_run_cmd="${docker_cmd} run -e AWS_DEFAULT_PROFILE=${AWS_DEFAULT_PROFILE:-default} -v ${HOME}/.aws:/root/.aws:ro"
elif [ -z "${AWS_ACCESS_KEY_ID-x}" ] || [ -z "${AWS_SECRET_ACCESS_KEY-x}" ]; then
    echo "Please set BOTH AWS_ACCESS_KEY_ID AND AWS_SECRET_ACCESS_KEY's if you choose to use AWS Access keys... exiting."
    exit 1
else
    # make sure region is set
    [ -z "${AWS_REGION-x}" ] && echo "Please set the \$AWS_REGION to use for drone. Either edit the .env file or `export AWS_REGION=us-east-1 ./bootstrap-drone.sh`" && exit 1
    docker_test_run_cmd="${docker_cmd} run -e AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} -e AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} -e AWS_REGION=${AWS_REGION}"
fi

# test aws-cli. `aws sts get-caller-identity` should return a value no matter what perms the calling user has
printf "Testing connectivity to AWS... "
$docker_test_run_cmd aws-cli sts get-caller-identity > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "OK"
    aws_cli="${docker_test_run_cmd} aws-cli"
else
    echo "FAIL"
    echo "Couldn't connect to AWS. Please check your crendentials and try again."
    exit 1
fi

# bootstrap
$aws_cli ec2 describe-images