#!/usr/bin/env bash
# RELEASES ARE FOUND AT https://github.com/docker/compose/releases

# INSTALL COMPOSE
# default to 1.24.0 if env var not set
COMPOSE_VERSION=${DOCKER_COMPOSE_VERSION:-1.24.0}

# install to /usr/local/bin
sudo curl -L "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# install bash-completion
sudo curl -L https://raw.githubusercontent.com/docker/compose/${COMPOSE_VERSION}/contrib/completion/bash/docker-compose -o /etc/bash_completion.d/docker-compose

# test install
ver=$(docker-compose --version > /dev/null 2>&1)
[ $? -eq 0 ] && echo "installed docker-compose" || exit 1
