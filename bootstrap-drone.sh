#!/usr/bin/env bash
# bootsraps an initial drone server. drone will subsequently 
# be used to build and deploy updates after that.
# set -x

##### SETTINGS ##########################################################################
# docker images
AWS_CLI_BASE_IMAGE="${AWS_CLI_BASE_IMAGE:-python:3.7}"
PACKER_BASE_IMAGE="${PACKER_BASE_IMAGE:-hashicorp/packer:latest}"
TERRAFORM_BASE_IMAGE="${TERRAFORM_BASE_IMAGE:-hashicorp/terraform:latest}"

# bootstrap credentials
AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID:-}
AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY:-}
AWS_DEFAULT_PROFILE=${AWS_DEFAULT_PROFILE:-}

# drone deployer credentials
DRONE_AWS_ACCESS_KEY_ID=${DRONE_BUILDER_AWS_ACCESS_KEY_ID:-}
DRONE_AWS_SECRET_ACCESS_KEY=${DRONE_BUILDER_AWS_SECRET_ACCESS_KEY:-}

# drone region and vpc
AWS_REGION=${AWS_REGION:-us-east-1}
DRONE_VPC_ID=${DRONE_VPC_ID:-}

# load settings from .env file if present
if [ -f ".env" ]; then
    source .env
fi

##### SETUP DOCKER + AWS-CLI|PACKER|TERRAFORM COMMAND IMAGES ############################
# set $docker_cmd (use sudo if root) and make sure docker is running
printf "Checking docker... "
docker_cmd=
if [ "$EUID" -eq 0 ]; then
    sudo docker images > /dev/null 2>&1 && docker_cmd='sudo docker'
else
    docker images > /dev/null 2>&1 && docker_cmd='docker'
fi
[ -z "${docker_cmd-x}" ] && echo "Can't connect to docker. Is it running?" && exit 1
echo "OK"

show_spinner()
{
    printf "pulling %s ... " "$2"
    local -r pid="${1}"
    local -r delay='0.75'
    local spinstr='\|/-'
    local temp
    while ps a | awk '{print $1}' | grep -q "${pid}"; do
        temp="${spinstr#?}"
        printf " [%c]  " "${spinstr}"
        spinstr=${temp}${spinstr%"${temp}"}
        sleep "${delay}"
        printf "\b\b\b\b\b\b"
    done
    printf "    \b\b\b\b"
    echo "OK"
}

("$@") &
show_spinner "$!"
# pre-pull images
printf "Pulling images:"
( $docker_cmd pull "$AWS_CLI_BASE_IMAGE" > /dev/null 2>&1 ) &
show_spinner "$!" "$AWS_CLI_BASE_IMAGE"
( $docker_cmd pull "$PACKER_BASE_IMAGE" > /dev/null 2>&1 ) &
show_spinner "$!" "$PACKER_BASE_IMAGE"
( $docker_cmd pull "$TERRAFORM_BASE_IMAGE" > /dev/null 2>&1 ) &
show_spinner "$!" "$TERRAFORM_BASE_IMAGE"


# build the aws-cli image if not present
$docker_cmd images | grep 'aws-cli' > /dev/null 2>&1
if [ $? -ne 0 ]; then
    printf "Building aws-cli image... "
    $docker_cmd build -f packer/aws-cli.Dockerfile -t aws-cli --build-arg CLI_BASE_IMAGE="${AWS_CLI_BASE_IMAGE}" packer/.
    [ $? -ne 0 ] && echo "Error building the aws-cli image... exiting." && exit 1
    echo "OK"
fi

# check aws creds (for bootstrapping the server only)
# use aws profile unless aws access keys are being used
if [ -z "${AWS_ACCESS_KEY_ID-x}" ] && [ -z "${AWS_SECRET_ACCESS_KEY-x}" ]; then
    # access keys are not being used.. mount local aws config and use profile instead
    docker_cmd="${docker_cmd} run -it --rm -e AWS_DEFAULT_PROFILE=${AWS_DEFAULT_PROFILE:-default} -v ${HOME}/.aws:/root/.aws:ro"
elif [ -z "${AWS_ACCESS_KEY_ID-x}" ] || [ -z "${AWS_SECRET_ACCESS_KEY-x}" ]; then
    echo "Please set BOTH AWS_ACCESS_KEY_ID AND AWS_SECRET_ACCESS_KEY's if you choose to use AWS Access keys... exiting."
    exit 1
else
    # access keys are set, make sure region is too
    [ -z "${AWS_REGION-x}" ] && echo "Please set the \$AWS_REGION to use for drone. Either edit the .env file or 'export AWS_REGION=us-east-1 ./bootstrap-drone.sh'" && exit 1
    docker_cmd="${docker_cmd} run -it --rm -e AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} -e AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} -e AWS_REGION=${AWS_REGION}"
fi

# test aws-cli. 
# note: `aws sts get-caller-identity` should return a value no matter what perms the calling user has, so it's good for testing
# connectivity with aws
printf "Checking aws connectivity... "
$docker_cmd aws-cli -- aws sts get-caller-identity > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "OK"
    aws="${docker_cmd} aws-cli -- aws"
else
    echo "FAIL"
    echo "Couldn't connect to AWS. Please check your crendentials and try again."
    exit 1
fi
# note: from now on use $aws for running aws commands.. e.g., `$aws ec2 describe-foo`


##### BOOTSTRAP #########################################################################

# ask for drone creds if not present
[ -z "${DRONE_AWS_ACCESS_KEY_ID+x}" ] || [ -z "${DRONE_AWS_SECRET_ACCESS_KEY+x}" ] && echo "Please enter the AWS credentials for the drone_builder user:"
if [ -z "${DRONE_AWS_ACCESS_KEY_ID+x}" ]; then
    read -rp 'AWS_ACCESS_KEY_ID:  ' DRONE_AWS_ACCESS_KEY_ID
fi
if [ -z "${DRONE_AWS_SECRET_ACCESS_KEY+x}" ]; then
    read -srp 'AWS_SECRET_ACCESS_KEY: ' DRONE_AWS_SECRET_ACCESS_KEY
fi

printf "\nGenerating unique drone-deployment-id: "
DRONE_DEPLOYMENT_ID=$(docker run -it --rm aws-cli /bin/sh -c "openssl rand -hex 16")
echo "${DRONE_DEPLOYMENT_ID}"

# fail if uuid is not at least 32 chars long
if (( ${#DRONE_DEPLOYMENT_ID} < 32 )); then
    echo "Failed to generate a 32 char UUID... exiting." && exit 1
fi

echo "Building AMI... "
packer_build_cmd="docker run -it --rm -v $(PWD)/packer:/tmp/packer --workdir=/tmp/packer hashicorp/packer:light build"

$packer_build_cmd \
        -var aws_access_key="${DRONE_AWS_ACCESS_KEY_ID}" \
        -var aws_secret_key="${DRONE_AWS_SECRET_ACCESS_KEY}" \
        -var drone_version="${DRONE_VERSION}" \
        -var drone_image="${DRONE_IMAGE}" \
        -var docker_compose_version="${DOCKER_COMPOSE_VERSION}" \
        -var drone_deployment_uuid="${DRONE_DEPLOYMENT_ID}" \
        podchaser_drone_server_ami.json
[ $? -ne 0 ] && echo "Failed to build AMI. Try running with 'bash -x ./bootstrap-drone.sh' to debug.. exiting." && exit 1

# get the latest ami id from the manifest file
echo ""
ami_id=$(docker run -it --rm -v "$(PWD)"/packer/manifest.json:/tmp/manifest.json aws-cli /bin/sh -c "cat /tmp/manifest.json | jq -r '.builds[-1].artifact_id' |  cut -d':' -f2")
echo "*** Don't forget to commit packer/manifest.json to git. ***"
echo $ami_id
