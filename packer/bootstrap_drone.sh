#!/usr/bin/env bash
DRONE_VERSION=${DRONE_VERSION:-1.0.7}
DRONE_IMAGE=${DRONE_IMAGE:-drone/drone:latest}

# pre-pull drone image
sudo docker pull "${DRONE_IMAGE}"

# install drone cli
curl -L "https://github.com/drone/drone-cli/releases/download/v${DRONE_VERSION}/drone_linux_amd64.tar.gz" | tar zx
sudo install -t /usr/local/bin drone
sudo chmod +x /usr/local/bin drone

# test drone cli install
drone -v > /dev/null 2>&1 && echo "installed drone cli" || exit 1
