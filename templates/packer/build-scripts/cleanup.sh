#!/usr/bin/env bash

printf "\n\n\n\n***** CLEANING UP *****\n\n\n\n"

export DEBIAN_FRONTEND=noninteractive
sudo apt-get -y autoremove
sudo apt-get -y clean
sudo rm -rf /tmp/*
history -c
