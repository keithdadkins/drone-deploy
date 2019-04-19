#!/usr/bin/env bash
# installs docker-compose
set -euo pipefail

printf "\n\n\n\n***** INSTALLING COMPOSE *****\n\n\n\n"

DOCKER_COMPOSE_VERSION=${DOCKER_COMPOSE_VERSION:-}
# you can find compose releases at https://github.com/docker/compose/releases

# fail if env vars are not set
var_fail_message="must be set in order to install docker-compose... exiting."
[ -z "$DOCKER_COMPOSE_VERSION" ] && echo "DOCKER_COMPOSE_VERSION $var_fail_message" && exit 1


# install to /usr/local/bin
sudo curl -L "https://github.com/docker/compose/releases/download/$DOCKER_COMPOSE_VERSION/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose


# install bash-completion
sudo curl -L "https://raw.githubusercontent.com/docker/compose/$DOCKER_COMPOSE_VERSION/contrib/completion/bash/docker-compose" -o /etc/bash_completion.d/docker-compose


# test install
if docker-compose --version > /dev/null 2>&1; then
    echo "Installed docker-compose"
else
    echo "Error installing docker-compose... exiting." && exit 1
fi