[![Build Status](https://drone.keithdadkins.me/api/badges/keithdadkins/drone-deploy/status.svg?ref=refs/heads/master)](https://drone.keithdadkins.me/keithdadkins/drone-deploy)

# Drone CI AWS EC2 deployer

__STATUS:__ This project is a work in progress and is in a pre-release state.

`drone-deploy` is a command line application used for spinning up [Drone CI](https://drone.io) servers on AWS. If you are an admin looking for a quick way to spin up one or more drone servers, and are comfortable with the cli, and have an AWS account with Route53 domain, then this may be useful to you.

__See it in action__

> TODO

## Overview

In short, `drone-deploy` app:

* Builds an Amazon Machine Image (AMI) based on the latest Ubuntu 18.04 LTS server with Docker, Compose, and Drone.
* Configures a web proxy (Caddy) with automatic TLS certificates using Let's Encrypt.
* Creates all the necessary AWS resources such as S3, IAM roles and policies, Route53 entries, etc.
* Deployment settings such as users, firewall rules, and server configurations, can be easily modified with a simple `config.yaml` file.
* Everything else can be customized by editing the various Packer, Terraform, and scripts located in the `/templates` directory.

I originally wrote this tool for a client so we could research and explore Drone - an inexpensive and easy way to self-host a cross-platform distributed CI/CD system. Basically, it's an altertative to Jenkins, Travis, that uses docker containers as build steps. Pretty neat.

Cost is cheap. For example, running [drone.keithdadkins.me](https://drone.keithdadkins.me) cost me around $5 - $10 a month (US) on a t2.micro instance. I use a few Mac and PC's around my office as build agents. But [anything running docker can become a build agent](TODO) so it's trivial to add more agents. There's also non-docker agents available for Mac, PC, Android, and other platforms as well.


## Requirements 

__Requirements for building the `drone-deploy` cli app__

* [Docker](https://www.docker.com/products/docker-desktop)
* [Python 3](https://realpython.com/installing-python/)
* [Terraform v0.11.14](https://learn.hashicorp.com/terraform/getting-started/install)
* Either have AWS cli tools installed or have secrets exported as env vars (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, etc)


__Requirements for running `drone-deploy` from release__

* Either have AWS cli tools installed or have secrets exported as env vars (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, etc)
* [Docker](https://www.docker.com/products/docker-desktop) for building the AMI
* [Terraform v0.11.14](https://learn.hashicorp.com/terraform/getting-started/install) for deploying resources.


## Docs
DOC | Location
----|----------
User Guide | [docs/drone-deploy user guide](docs/drone-deploy-user-guide.md)
Developer Guide | [docs/drone-deploy developer guide](docs/drone-deploy-developer-guide.md)
