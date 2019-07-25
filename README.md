[![Build Status](https://drone.keithdadkins.me/api/badges/keithdadkins/drone-deploy/status.svg?ref=refs/heads/master)](https://drone.keithdadkins.me/keithdadkins/drone-deploy)

# drone-deploy cli-app

The `drone-deploy` cli application builds, deploys, and maintains [Drone.io](https://drone.io) CI/CD installations on AWS. Specifically, the cli app:

* Builds a reasonably hardened Ubuntu 18.04 Amazon Machine Image (using the latest official Ubuntu AMI)
* Installs docker, docker-compose, and drone along with automatic TLS cert setup for https://drone.yourdomain.com.
* Creates all the necessary IAM Roles and Policies for the drone-server.
* Creates a hardened S3 bucket for storing build logs and backups.
* Generates and attaches an Elastic IP (EIP) along with a Route53 DNS entry for drone.yourdomain.com.
* Generates appropriate firewall (security group) rules to enable http, https, and ssh access from the ip addresse(s) you specify.
* Uses AWS Parameter store for storing and managing secrets

## `drone-deploy` Requirements

* (Docker)[https://www.docker.com/products/docker-desktop]
* (Python 3)[https://realpython.com/installing-python/]
* (Terraform v11)[https://learn.hashicorp.com/terraform/getting-started/install]

## `drone-deploy` setup

```bash
git clone foo
cd foo
make
```
