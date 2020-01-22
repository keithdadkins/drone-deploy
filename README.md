[![Build Status](https://drone-deploy.keithdadkins.me/api/badges/keithdadkins/drone-deploy/status.svg?ref=refs/heads/master)](https://drone-deploy.keithdadkins.me/keithdadkins/drone-deploy/) [![license](https://img.shields.io/github/license/keithdadkins/drone-deploy)](https://github.com/keithdadkins/drone-deploy/blob/master/LICENSE) [![release](https://img.shields.io/github/release/keithdadkins/drone-deploy)](https://github.com/keithdadkins/drone-deploy/releases/)

# drone-deploy  

__A standalone Drone CI deployment tool for AWS.__

__STATUS:__ *This project is not actively maintained and is not ready for any type of production use.*

`drone-deploy` is a (MacOS/Linux) command line application used for spinning up [Drone CI](https://drone.io) servers on AWS. If you are an admin looking for a quick way to deploy and manage one or more drone servers, are comfortable with the cli, and have an AWS account with Route53 domain, then this may be useful to you.

__See it in action__

> TODO

## Overview

In short, `drone-deploy`:

* Builds an Amazon Machine Image (AMI) based on the latest Ubuntu 18.04 LTS server with Docker, Compose, and Drone.
* Configures a web proxy (Caddy) with automatic TLS certificates for your custom domain using Let's Encrypt.
* Creates all the necessary AWS resources such as S3, IAM roles and policies, Route53 entries, etc.
* Deployment settings such as users, firewall rules, and server configurations, can be easily modified with a simple `config.yaml` file.
* Everything else can be customized by editing the various Packer, Terraform, and scripts located in the `/templates` directory.

I originally wrote this tool for a client so we could research and explore Drone - an inexpensive and easy way to self-host a cross-platform distributed CI/CD system. Basically, it's an altertative to Jenkins, Travis, or similar that uses docker containers as build steps. Pretty neat.

Cost is cheap. For example, running [drone-deploy.keithdadkins.me](https://drone-deploy.keithdadkins.me/keithdadkins/drone-deploy/) costs around $5 - $10 a month (US) on a t2.micro instance. I use a few Mac and PC's around my office as build agents, but [anything running docker can become a build agent](TODO) so it's trivial to add more agents from anywhere. If you need to build outside of the docker imposed linux platform, non-docker agents are available as well (MacOS, Windows, Android, etc).

## Requirements

__Requirements for running `drone-deploy` from release__

* [Docker](https://www.docker.com/products/docker-desktop) for building the AMI
* [Terraform v0.11.14](https://learn.hashicorp.com/terraform/getting-started/install) for deploying resources.

__Requirements for building, running, developing `drone-deploy` from source__

* [Docker](https://www.docker.com/products/docker-desktop)
* [Python 3](https://realpython.com/installing-python/)
* [Terraform v0.11.14](https://learn.hashicorp.com/terraform/getting-started/install)

## Docs

DOC | Location
----|----------
User Guide | [docs/drone-deploy user guide](docs/drone-deploy-user-guide.md)
Developer Guide | [docs/drone-deploy developer guide](docs/drone-deploy-developer-guide.md)
