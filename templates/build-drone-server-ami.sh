#!/usr/bin/env bash
# Builds the drone server amazon machine image.
# Usage: build-drone-server-ami.sh [-h|--help] [-p|--profile] [--no-cache] [--rm]

set -euo pipefail

# aws credentials (use --profile if set, else uses access keys)
AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID:-}"
AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY:-}"
AWS_PROFILE="${AWS_PROFILE:-}"
unset AWS_SESSION_TOKEN

# builder creds
DRONE_BUILDER_ROLE_ARN="${DRONE_BUILDER_ROLE_ARN:-}"
DRONE_BUILDER_AWS_ACCESS_KEY_ID="${DRONE_BUILDER_AWS_ACCESS_KEY_ID:-}"
DRONE_BUILDER_AWS_SECRET_ACCESS_KEY="${DRONE_BUILDER_AWS_SECRET_ACCESS_KEY:-}"

# drone settings
DRONE_DEPLOYMENT_NAME="${DRONE_DEPLOYMENT_NAME:-}"
DRONE_CLI_VERSION="${DRONE_CLI_VERSION:-}"
DRONE_DOCKER_COMPOSE_VERSION="${DRONE_DOCKER_COMPOSE_VERSION:-}"
DRONE_AWS_REGION="${DRONE_AWS_REGION:-}"
DRONE_SERVER_DOCKER_IMAGE="${DRONE_SERVER_DOCKER_IMAGE:-}"
DRONE_AGENT_DOCKER_IMAGE="${DRONE_AGENT_DOCKER_IMAGE:-}"
DRONE_SERVER_HOST="${DRONE_SERVER_HOST:-}"
DRONE_RPC_SECRET="${DRONE_RPC_SECRET:-}"
DRONE_VPC_ID="${DRONE_VPC_ID:-}"
DRONE_ADMIN="${DRONE_ADMIN:-}"
DRONE_ADMIN_EMAIL="${DRONE_ADMIN_EMAIL:-}"
DRONE_USER_FILTER="${DRONE_USER_FILTER:-}"
DRONE_GITHUB_CLIENT_ID="${DRONE_GITHUB_CLIENT_ID:-}"
DRONE_GITHUB_CLIENT_SECRET="${DRONE_GITHUB_CLIENT_SECRET:-}"
DRONE_S3_BUCKET="${DRONE_S3_BUCKET:-}"


# defaults for docker images
AWS_CLI_BASE_IMAGE="${AWS_CLI_BASE_IMAGE:-python:3.7}"
PACKER_BASE_IMAGE="${PACKER_BASE_IMAGE:-hashicorp/packer:latest}"
TERRAFORM_BASE_IMAGE="${TERRAFORM_BASE_IMAGE:-hashicorp/terraform:latest}"

# cli options
# PURGE == remove docker images at end
# REBUILD == rebuild docker images from scratch
PURGE="false"
REBUILD="false"

# globals
aws=
docker=

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
    echo -e "Usage: build-drone-server-ami.sh [-h|--help] [-n|--no-cache] [-p|--profile [name]] [--rm]"
}

help_message() {
    cat <<- _EOF_
    build-drone-server-ami.sh
    Bootstraps a packer ec2 instance and builds the drone-server amazon machine image.
    $(usage)

    Options:
    -h, --help    Display this help message and exit.
    --no-cache    Don't use cached images. Rebuild from scratch.
    --rm          Remove docker images downloaded/created during the build.
    -p, --profile [profile-name] 
                  Use a configured aws profile instead of access keys. Uses 'default' profile if name not given.
                  The profile must not be a root account holder profile (root accounts cannot AssumeRole).
    
    Examples:
    Edit and source the .env file.
    $> . .env

    Build using AWS access keys
    $> AWS_ACCESS_KEY_ID='ABCD123452JIMTAMQGU2' AWS_SECRET_ACCESS_KEY='ABCDeLjflnVj+1234567/fooBARsqwDAQTtCmI' ./build-drone-server-ami.sh

    Build using your default AWS profile (~/.aws/credentials) and remove bootstrap docker images when done
    ./build-drone-server-ami.sh -p --rm

    Build using a named profile and rebuild docker-images instead of using cached images.
    ./build-drone-server-ami.sh --profile prod --no-cache

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


# builds a docker command with our temporary aws credentials set as env vars
get_aws_command(){
    local aws_cmd=

    # configure AWS_PROFILE if provided, else use access keys in the docker command
    if [ -z "$AWS_PROFILE" ]; then
        aws_cmd="$docker run --rm -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY aws-cli -- aws"
    else
        aws_cmd="$docker run --rm -v ${HOME}/.aws:/root/.aws:ro -e AWS_DEFAULT_PROFILE=$AWS_PROFILE aws-cli -- aws"
    fi
    echo "$aws_cmd"
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
        if ! $docker build -f packer/aws-cli/aws-cli.Dockerfile -t aws-cli --no-cache --build-arg CLI_BASE_IMAGE="$AWS_CLI_BASE_IMAGE" packer/aws-cli/.; then
            echo "Error building dockerfile... exiting." && exit 1
        fi
        exec 1>&3 3>&-
        echo "    DONE"
    fi
}


# assumes the IAM role that Packer uses during AMI creation and exports a set of temp aws credentials that we pass to packer
generate_build_credentials(){

    # The user running this script must have permissions to assume the drone-builder role in order to bootstrap packer
    local temp_creds=
    temp_creds="$($aws sts assume-role --role-arn "$DRONE_BUILDER_ROLE_ARN" --role-session-name $DRONE_DEPLOYMENT_NAME-builder)"
    #     echo "Unable to perform the AssumeRole operation for the current user."
    #     exit 1
    # fi

    DRONE_BUILDER_AWS_ACCESS_KEY_ID=$($docker run --rm aws-cli /bin/sh -c "echo '$temp_creds' | jq .Credentials.AccessKeyId | xargs")
    DRONE_BUILDER_AWS_SECRET_ACCESS_KEY=$($docker run --rm aws-cli /bin/sh -c "echo '$temp_creds' | jq .Credentials.SecretAccessKey | xargs")
    DRONE_BUILDER_AWS_SESSION_TOKEN=$($docker run --rm aws-cli /bin/sh -c "echo '$temp_creds' | jq .Credentials.SessionToken | xargs")
    export DRONE_BUILDER_AWS_ACCESS_KEY_ID
    export DRONE_BUILDER_AWS_SECRET_ACCESS_KEY
    export DRONE_BUILDER_AWS_SESSION_TOKEN
}


# generates 32 character uuid
generate_uuid(){
    local uuid=
    uuid=$($docker run --rm aws-cli /bin/sh -c "openssl rand -hex 16")

    # error if uuid is not at least 32 chars long
    if (( ${#uuid} < 32 )); then
        return 1
    fi
    echo "$uuid"   
}


# adds a non-encrypted parameter to aws parameter store
put_parameter(){
    local key=      # $1 == key
    local value=    # $2 == value
    key="${1:-}"
    value="${2:-}"

    # return error if no key or value (paramater store requires a non-null, non-blank value)
    if [ -z "$key" ] || [ -z "$value" ]; then 
        return 2
    fi

    # put the parameter
    printf "    adding '$key'... "
    if $aws ssm put-parameter --name "$key" --value "$value" --type String --region "$DRONE_AWS_REGION" > /dev/null 2>&1; then
        echo "OK"
    else
        echo "X"
        return 1
    fi
}


# adds an encrypted paramater to aws paramater store
put_secret_parameter(){
    local key=      # $1 == key
    local value=    # $2 == value
    key="${1:-}"
    value="${2:-}"

    # return error if no key or value (paramater store requires a non-null, non-blank value)
    if [ -z "$key" ] || [ -z "$value" ]; then 
        return 2
    fi

    # put the parameter
    printf "    adding secret '$key'... "
    if $aws ssm put-parameter --name "$key" --value "$value" --type SecureString --region "$DRONE_AWS_REGION" > /dev/null 2>&1; then
        echo "OK"
    else
        echo "X"
        return 1
    fi
}


# builds the ami
build_drone_server_ami(){
    echo "Building AMI... "
    packer_build_cmd="$docker run --rm -v $(PWD)/packer:/tmp/packer --workdir=/tmp/packer hashicorp/packer:light build"
    # note: ${VARNAME%%[[:cntrl:]]} removes trailing /r's from strings. dang tty's.

    # note: ${VARNAME%%[[:cntrl:]]} removes trailing /r's from strings. dang tty's.
    $packer_build_cmd \
        -var aws_access_key="${DRONE_BUILDER_AWS_ACCESS_KEY_ID%%[[:cntrl:]]}" \
        -var aws_secret_key="${DRONE_BUILDER_AWS_SECRET_ACCESS_KEY%%[[:cntrl:]]}" \
        -var aws_session_token="${DRONE_BUILDER_AWS_SESSION_TOKEN%%[[:cntrl:]]}" \
        -var drone_deployment_uuid="${DRONE_DEPLOYMENT_ID%%[[:cntrl:]]}" \
        -var drone_aws_region="$DRONE_AWS_REGION" \
        -var aws_region="$DRONE_AWS_REGION" \
        -var drone_cli_version="$DRONE_CLI_VERSION" \
        -var drone_server_docker_image="$DRONE_SERVER_DOCKER_IMAGE" \
        -var drone_agent_docker_image="$DRONE_AGENT_DOCKER_IMAGE" \
        -var drone_docker_compose_version="$DRONE_DOCKER_COMPOSE_VERSION" \
        -var iam_instance_profile="$DRONE_DEPLOYMENT_NAME-builder" \
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

    # set aws command
    aws="$(get_aws_command)"

    # pull command images and build the aws-cli image
    echo "Preparing to build: "
    pull_image "$AWS_CLI_BASE_IMAGE" && echo "OK"
    pull_image "$PACKER_BASE_IMAGE" && echo "OK"
    pull_image "$TERRAFORM_BASE_IMAGE" && echo "OK"
    # build_aws_cli_image

    # assume the builder role and generate temp aws credentials
    generate_build_credentials

    # generate a unique deployment id for tagging drone resources
    if [ -z "$DRONE_DEPLOYMENT_ID" ]; then
        printf "Generating unique drone-deployment-id: "
        if deployment_id="$(generate_uuid)"; then
            export DRONE_DEPLOYMENT_ID="$deployment_id"
            echo "$DRONE_DEPLOYMENT_ID"
        else
            echo "Error generating drone-deployment-id... exiting."
        fi
    else
        echo "Using $DRONE_DEPLOYMENT_ID."
    fi

    # generate a unique DRONE_RPC_SECRET uuid (if not provided)
    if [ -z "$DRONE_RPC_SECRET" ]; then
        printf "Generating unique drone rpc uuid... "
        if DRONE_RPC_SECRET="$(generate_uuid)"; then
            echo "********************************"
        else
            echo "Error generating RPC UUID... exiting." && exit 1
        fi
    else
        echo "Using \$DRONE_RPC_SECRET environment variable."
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
        echo "Failed to build AMI. Try running with 'bash -x ./build-drone-server-ami.sh' to debug script.. exiting."
        exit 1
    fi

    # add our configs to parameter store
    echo "Adding configs to parameter store: "
    aws=$(get_aws_command)
    local prefix=
    prefix="/drone/$DRONE_DEPLOYMENT_ID"

    # non-secret paramaters
    set -x
    put_parameter "$prefix/DRONE_AWS_REGION" "$DRONE_AWS_REGION"
    put_parameter "$prefix/DRONE_SERVER_HOST" "'$DRONE_SERVER_HOST'"
    put_parameter "$prefix/DRONE_SERVER_DOCKER_IMAGE" "'$DRONE_SERVER_DOCKER_IMAGE'"
    put_parameter "$prefix/DRONE_AGENT_DOCKER_IMAGE" "'$DRONE_AGENT_DOCKER_IMAGE'"

    # secret paramaters
    put_secret_parameter "$prefix/DRONE_ADMIN" "$DRONE_ADMIN"
    put_secret_parameter "$prefix/DRONE_ADMIN_EMAIL" "$DRONE_ADMIN_EMAIL"
    put_secret_parameter "$prefix/DRONE_USER_FILTER" "$DRONE_USER_FILTER"
    put_secret_parameter "$prefix/DRONE_RPC_SECRET" "$DRONE_RPC_SECRET"
    put_secret_parameter "$prefix/DRONE_GITHUB_CLIENT_ID" "$DRONE_GITHUB_CLIENT_ID"
    put_secret_parameter "$prefix/DRONE_GITHUB_CLIENT_SECRET" "$DRONE_GITHUB_CLIENT_SECRET"
    echo "Done. The uploaded parameters will be used by the drone server instance during launch."
}

##### script entrypoint below #####

# parse command line args
while [[ -n ${1:-} ]]; do
    case $1 in
        -h | --help) help_message; graceful_exit ;;
        -p | --profile)
            if [ -z "${2:-}" ] || [[ "${2:-}" == -* ]]; then
                AWS_PROFILE="default"
            else
                shift; AWS_PROFILE="$1"
            fi
        ;;
        --no-cache) REBUILD="true" ;;
        --rm) PURGE="true" ;;
        --* | -*) usage; error_exit "Unknown option $1" ;;
        *) usage; error_exit "Unknown argument $1" ;;
    esac
    shift
done

# start the build & exit if successful
build
graceful_exit
