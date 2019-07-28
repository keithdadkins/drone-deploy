[![Build Status](https://drone.keithdadkins.me/api/badges/keithdadkins/drone-deploy/status.svg?ref=refs/heads/master)](https://drone.keithdadkins.me/keithdadkins/drone-deploy)

# Drone CI AWS EC2 deployer

This project builds a command-line application `drone-deploy`, which builds, configures, and deploys one or more Drone-CI server instances on AWS.

The primary goals of this project:
    - Make it super easy to spin up and down build clusters by automating the boring stuff (EC2, DNS, IAM, TLS, etc)
    - Find an inexpensive way of self-hosting large build clusters using remote agents.
    - Explore and learn DroneCI.
    - And build my first non-trivial Python application.

### `drone-deploy` CLI Overview

The `drone-deploy` cli app is used to manage one or more drone server __'deployments'__. More specifically, it (using Packer, Terraform, bash scripts, etc) builds, deploys, and configures an Amazon EC2 instance to run a dedicated DroneCI server along with a custom domain name and https certificates.


Here are some example commands to give you an idea of how the app works, but please refer to the [drone-deploy user guide](./drone-deploy-user-guide.md) for detailed instructions.

```shell
$> drone-deploy new acme-builder.keithdadkins.me
Deployment created: /Users/foo/drone-deploy/deployments/acme-builder.keithdadkins.me
Next steps:
  - edit the config.yaml file ('drone-deploy edit acme-builder.keithdadkins.me')
  - run 'drone-deploy prepare acme-builder.keithdadkins.me' to bootstrap the deployment.
  - run 'drone-deploy build-ami acme-builder.keithdadkins.me' to build the drone-server ami.
  - run 'drone-deploy plan acme-builder.keithdadkins.me' and review.
  - run 'drone-deploy apply acme-builder.keithdadkins.me' to deploy.

$> drone-deploy deploy acme-builder.keithdadkins.me
Deploying acme-builder.keithdadkins.me...
...
```

After github and the server is configured and running, you can then launch build agents from anywhere docker is running (the office, your house, other EC2 instances, etc) by running a specific docker command (which you get by running `drone-deploy show-agent-command`). Example:

```shell
$> drone-deploy show-agent-command acme-builder.keithdadkins.me

        # Run the following command on a host running docker to launch a build agent:

        docker run -v /var/run/docker.sock:/var/run/docker.sock \
            -e DRONE_RPC_SERVER=https://acme-builder.keithdadkins.me \
            -e DRONE_RUNNER_CAPACITY=1 \
            -e DRONE_RPC_SECRET=40729087a50f610874bb36e25c6ba122 \
            -d drone/agent:latest
```

Copy and paste the command on a box running docker and the drone server will be able to distribute builds to that agent as long as the docker command is running.


### Deployment Overview

The primary goal of a deployment is to:

* Build a reasonably hardened Ubuntu 18.04 Amazon Machine Image (using the latest official Ubuntu AMI).
* Create all the necessary Amazon IAM Roles and Policies.
* Generate and attach an Elastic IP (EIP), Route53 DNS entry, and Route53 domain for the server. E.g. https://drone.yourdomain.com
* Configure and deploy the drone server EC2 instance, along with automatic TLS cert registration (via Let's Encrypt) for your custom route53 domain https://drone.yourdomain.com,
* Create a secured S3 bucket for storing build logs and backups.
* Generate firewall/security group rules to enable http, https, and ssh access from the ip address(es) you specify.
* Use AWS Parameter store for storing and transmitting secrets securely.

### Requirements for building the cli

* (Docker)[https://www.docker.com/products/docker-desktop]
* (Python 3)[https://realpython.com/installing-python/]
* (Terraform v0.11.14)[https://learn.hashicorp.com/terraform/getting-started/install]

### Requirements for running the cli

* (Docker)[https://www.docker.com/products/docker-desktop] for building the AMI
* (Terraform v0.11.14)[https://learn.hashicorp.com/terraform/getting-started/install] for deploying resources.


## Building the CLI

1. 
2. 
3. To enable bash auto-completion: `eval "$(_DRONE_DEPLOY_COMPLETE=source drone-deploy)"`

## Using the CLI

Please refer to the __[drone-deploy user guide](./drone-deploy-user-guide.md)__ on how to use `drone-deploy`.
