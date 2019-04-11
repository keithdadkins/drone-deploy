#!/usr/bin/env bash
# installs docker-ce on Ubuntu 18.04 LTS (amd64)
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    wget \
    software-properties-common

# add docker's ubuntu repo
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu bionic stable"

# install docker
sudo apt-get update
sudo apt-get install -y docker-ce

# only install docker from dockers repo
sudo apt-cache policy docker-ce

# fix perms
sudo usermod -aG docker ubuntu
