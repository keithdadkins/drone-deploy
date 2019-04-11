#!/usr/bin/env bash
echo 'Cleaning up after provisioning... '

export DEBIAN_FRONTEND=noninteractive
sudo apt-get -y autoremove && \
sudo apt-get -y clean && \
sudo rm -rf /tmp/*
history -c
