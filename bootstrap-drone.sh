#!/usr/bin/env bash
# Builds and bootstraps the drone server amazon machine image.
# Usage: bootstrap-drone.sh [-h|--help] [-n|--no-cache] [-p|--purge]

set -euo pipefail
unset AWS_SESSION_TOKEN

# drone settings
DRONE_REGION="${DRONE_REGION:-}"
DRONE_VPC_ID="${DRONE_VPC_ID:-}"
DRONE_BUILDER_ROLE_ARN="${DRONE_BUILDER_ROLE_ARN:-}"
DRONE_SERVER_ROLE_ARN="${DRONE_SERVER_ROLE_ARN:-}"
DRONE_BUILDER_AWS_ACCESS_KEY_ID="${DRONE_BUILDER_AWS_ACCESS_KEY_ID:-}"
DRONE_BUILDER_AWS_SECRET_ACCESS_KEY="${DRONE_BUILDER_AWS_SECRET_ACCESS_KEY:-}"

# defaults for docker images
AWS_CLI_BASE_IMAGE="${AWS_CLI_BASE_IMAGE:-python:3.7}"
PACKER_BASE_IMAGE="${PACKER_BASE_IMAGE:-hashicorp/packer:latest}"
TERRAFORM_BASE_IMAGE="${TERRAFORM_BASE_IMAGE:-hashicorp/terraform:latest}"

# cli options
# PURGE == remove docker images at end
# REBUILD == rebuild docker images from scratch
PURGE="false"
REBUILD="false"

#### basic shell functions (error trapping, handeling, arg parsing)
clean_up() {
    if [ "$PURGE" == "true" ]; then
        echo "Removing docker images... "
        $docker rmi "$AWS_CLI_BASE_IMAGE"
        $docker rmi "$PACKER_BASE_IMAGE"
        $docker rmi "$TERRAFORM_BASE_IMAGE"
    fi
    # TODO check for orphaned ec2 resources
    # TODO check for orphaned containers
}

error_exit(){
    clean_up && exit 1 
}

graceful_exit(){
    echo "Don't forget to commit the build manifest to git (./packer/manifest.json) for reference."
    clean_up && exit 
}

# handle trapped os signals
signal_exit(){
    case $1 in
        INT) error_exit "Build interrupted by user." ;;
        TERM) graceful_exit ;;
        *) error_exit ;;
    esac
}

usage() {
    echo -e "Usage: bootstrap-drone.sh [-h|--help] [-n|--no-cache] [-p|--purge]"
}

help_message() {
    cat <<- _EOF_
    bootstrap-drone.sh
    builds and bootstraps a drone-server AMI on AWS.
    $(usage)

    Options:
    -h, --help  Display this help message and exit.
    -n, --no-cache  Don't use cached images. Rebuild from scratch.
    -p, --purge  Remove docker images downloaded/created during the build.

_EOF_
    return
}

# trap signals
trap "signal_exit TERM" TERM HUP
trap "signal_exit INT"  INT


# utility function to display a spinner when doing long running tasks
show_spinner(){
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
}


# set the $docker command to use throughout the script (e.g., uses sudo if run as root)
get_docker_cmd(){
    local docker_cmd='docker'
    [ "$EUID" -eq 0 ] && docker_cmd="sudo docker"
    echo "$docker_cmd"
}


# pulls a docker image without all the verbose output
pull_image(){
    # $1 == docker image e.g., 'hashicorp/packer:latest'
    printf "    pulling %s ... " "$1"
    ( $docker pull "$1" > /dev/null 2>&1 ) &
    show_spinner "$!"
}


# builds the aws-cli image for running commands (see packer/aws-cli.Dockerfile)
build_aws_cli_image(){
    # rebuild if --no-cache is set
    if [ "$REBUILD" == "false" ] && $docker images | grep 'aws-cli' > /dev/null 2>&1; then
        echo "    aws-cli image found in cache... OK"
    else
        printf "    building aws-cli image... "
        # the exec redirect/paste stuff is just a hack to move the build output over some for formatting purposes
        exec 3>&1
        exec 1> >(paste /dev/null -)
        if ! $docker build -f packer/aws-cli.Dockerfile -t aws-cli --build-arg --no-cache CLI_BASE_IMAGE="$AWS_CLI_BASE_IMAGE" packer/.; then
            echo "Error building dockerfile... exiting." && exit 1
        fi
        exec 1>&3 3>&-
        echo "    DONE"
    fi
}


# assumes the IAM role that Packer uses during AMI creation and exports a set of temp aws credentials that we pass to packer
generate_build_credentials(){
    # The user running this script must have permissions to assume the DroneBuilder role and
    # permissions to pass the DroneServer role as well. See README.md for more info.
    local temp_role=
    temp_role="$(aws sts assume-role --role-arn "$DRONE_BUILDER_ROLE_ARN" --role-session-name "drone-builder")"

    DRONE_BUILDER_AWS_ACCESS_KEY_ID=$($docker run --rm aws-cli /bin/sh -c "echo '$temp_role' | jq .Credentials.AccessKeyId | xargs")
    DRONE_BUILDER_AWS_SECRET_ACCESS_KEY=$($docker run --rm aws-cli /bin/sh -c "echo '$temp_role' | jq .Credentials.SecretAccessKey | xargs")
    DRONE_BUILDER_AWS_SESSION_TOKEN=$($docker run --rm aws-cli /bin/sh -c "echo '$temp_role' | jq .Credentials.SessionToken | xargs")
    export DRONE_BUILDER_AWS_ACCESS_KEY_ID
    export DRONE_BUILDER_AWS_SECRET_ACCESS_KEY
    export DRONE_BUILDER_AWS_SESSION_TOKEN
}


# builds a docker command with our temporary aws credentials set as env vars
get_aws_command(){
    local session_creds="-e AWS_SESSION_TOKEN=$DRONE_BUILDER_AWS_SESSION_TOKEN -e AWS_ACCESS_KEY_ID=$DRONE_BUILDER_AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY=$DRONE_BUILDER_AWS_SECRET_ACCESS_KEY" 
    echo "$docker $session_creds run --rm aws-cli -- aws"
}


# generates a unique deployment uuid
generate_deployment_uuid(){
    local uuid=
    uuid=$($docker run --rm aws-cli /bin/sh -c "openssl rand -hex 16")

    # fail if uuid is not at least 32 chars long
    if (( ${#uuid} < 32 )); then
        echo "Failed to generate a 32 char UUID... exiting." && exit 1
    fi
    echo "$uuid"
}


# builds the ami using packer - ./packer/drone_server_ami.json
build_drone_server_ami(){
    echo "Building AMI... "
    packer_build_cmd="$docker run --rm -v $(PWD)/packer:/tmp/packer --workdir=/tmp/packer hashicorp/packer:light build"

    # note: ${VARNAME%%[[:cntrl:]]} removes trailing /r's from strings. dang tty's.
    $packer_build_cmd \
        -var aws_access_key="${DRONE_BUILDER_AWS_ACCESS_KEY_ID%%[[:cntrl:]]}" \
        -var aws_secret_key="${DRONE_BUILDER_AWS_SECRET_ACCESS_KEY%%[[:cntrl:]]}" \
        -var aws_session_token="${DRONE_BUILDER_AWS_SESSION_TOKEN%%[[:cntrl:]]}" \
        -var drone_deployment_uuid="${DRONE_DEPLOYMENT_ID%%[[:cntrl:]]}" \
        -var aws_region="$DRONE_REGION" \
        -var drone_region="$DRONE_REGION" \
        -var drone_version="$DRONE_VERSION" \
        -var drone_image="$DRONE_IMAGE" \
        -var docker_compose_version="$DOCKER_COMPOSE_VERSION" \
        -var iam_instance_profile="DroneBuilderInstanceProfile" \
        packer_build_drone_server_ami.json
}


# gets the latest ami id from ./packer/manifest.json (which is generated during builds)
get_and_validate_ami_id(){
    local ami_id=
    local last_run_uuid=
    local current_run_uuid=
    ami_id=$($docker run --rm -v "$(PWD)"/packer/manifest.json:/tmp/manifest.json aws-cli /bin/sh -c "cat /tmp/manifest.json | jq -r '.builds[-1].artifact_id' |  cut -d':' -f2")
    last_run_uuid=$($docker run --rm -v "$(PWD)"/packer/manifest.json:/tmp/manifest.json aws-cli /bin/sh -c "cat /tmp/manifest.json | jq -r '.last_run_uuid' |  cut -d':' -f2")
    current_run_uuid=$($docker run --rm -v "$(PWD)"/packer/manifest.json:/tmp/manifest.json aws-cli /bin/sh -c "cat /tmp/manifest.json | jq -r '.builds[-1].packer_run_uuid' |  cut -d':' -f2")
    
    # make sure last and current run uuid's match in packer/manifest.json
    if [ "$last_run_uuid" == "$current_run_uuid" ]; then
        echo "$ami_id"
    else
        echo "ERROR: packer/manifest.json's last_run_uuid and packer_run_uuid should match... exiting."
        return 1
    fi
}


build(){
    # configure docker command and make sure it's running
    docker="$(get_docker_cmd)"
    if ! $docker images > /dev/null 2>&1; then
        $docker info
    fi

    # pull command images and build the aws-cli image
    echo "Prepping bootstrap: "
    pull_image "$AWS_CLI_BASE_IMAGE" && echo "OK"
    pull_image "$PACKER_BASE_IMAGE" && echo "OK"
    pull_image "$TERRAFORM_BASE_IMAGE" && echo "OK"
    build_aws_cli_image

    # assume the builder role and generate temp aws credentials
    generate_build_credentials

    # generate a 32 character unique uuid for tagging drone resources
    printf "Generating unique drone-deployment-id: "
    if ! deployment_id=$(generate_deployment_uuid); then
        echo "Unable to generate UUID."
        echo "$deployment_id"
        exit 1
    else
        export DRONE_DEPLOYMENT_ID="$deployment_id"
        echo "$DRONE_DEPLOYMENT_ID"
    fi

    # build the server ami and validate
    if build_drone_server_ami; then
        # get the ami id and validate (ensure manifest.json is synced to disk first)
        sync
        if ! ami_id="$(get_and_validate_ami_id)"; then
            echo "$ami_id" && exit 1
        else
            export AMI_ID="${ami_id%%[[:cntrl:]]}"
        fi
    else
        echo "Failed to build AMI. Try running with 'bash -x ./bootstrap-drone.sh' to debug script.. exiting."
        exit 1
    fi
}

##### script entrypoint below #####

# parse command line args
while [[ -n ${1:-} ]]; do
    case $1 in
        -h | --help) help_message; graceful_exit ;;
        -n | --no-cache) REBUILD="true" ;;
        -p | --purge) PURGE="true" ;;
        --* | -*) usage; error_exit "Unknown option $1" ;;
        *) usage; error_exit "Unknown argument $1" ;;
    esac
    shift
done

# start the build & exit if successful
build
graceful_exit
