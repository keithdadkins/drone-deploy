#!/usr/bin/env bash
DRONE_CLI_VERSION=${DRONE_CLI_VERSION:-}
DRONE_SERVER_DOCKER_IMAGE=${DRONE_SERVER_DOCKER_IMAGE:-}
DRONE_AGENT_DOCKER_IMAGE=${DRONE_AGENT_DOCKER_IMAGE:-}
set -euo pipefail

printf "\n\n\n\n***** INSTALLING DRONE *****\n\n\n\n"

# fail if env vars are not set
var_fail_message="must be set in order to continue... exiting."
[ -z "$DRONE_CLI_VERSION" ] && echo "DRONE_AWS_VERSION $var_fail_message" && exit 1
[ -z "$DRONE_SERVER_DOCKER_IMAGE" ] && echo "DRONE_SERVER_DOCKER_IMAGE $var_fail_message" && exit 1
[ -z "$DRONE_AGENT_DOCKER_IMAGE" ] && echo "DRONE_AGENT_DOCKER_IMAGE $var_fail_message" && exit 1


# set our $aws command (just a shortcut instead of writing out a long docker run command everytime)
get_docker_cmd(){
    local docker_cmd='docker'
    [ "$EUID" -eq 0 ] && docker_cmd="sudo docker"
    echo "$docker_cmd"
}
docker="$(get_docker_cmd)"
aws="$docker run --rm aws-cli -- aws"


# pre-pull drone images
$docker pull "$DRONE_SERVER_DOCKER_IMAGE"
$docker pull "$DRONE_AGENT_DOCKER_IMAGE"


# install drone cli
curl -L "https://github.com/drone/drone-cli/releases/download/v$DRONE_CLI_VERSION/drone_linux_amd64.tar.gz" | tar zx
sudo install -t /usr/local/bin drone
sudo chmod +x /usr/local/bin drone

# test drone cli install
if drone -v > /dev/null 2>&1; then
    echo "installed drone cli"
else
    echo "Error installing drone cli... exiting." && exit 1
fi
