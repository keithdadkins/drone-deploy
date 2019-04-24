[![Build Status](https://drone.keithdadkins.me/api/badges/keithdadkins/drone.podchaser.com/status.svg?ref=refs/heads/master)](https://drone.keithdadkins.me/keithdadkins/drone.podchaser.com)

# Drone

This projects builds, deploys, and maintains a [Drone.io](https://drone.io) CI/CD installation on AWS. Specifically, it..

* Creates all the necessary IAM Roles, Policies, and Instance Profiles to deploy drone without embedding AWS access keys.
* Builds a hardened Ubuntu 18.04 Amazon Machine Image (AMI) with docker, docker-compose, and drone ready to go with automatic TLS certs for https://drone.yourdomain.com.
* Creates a locked-down S3 bucket for storing build logs, tls certs, and database backups. Only the admin and the drone server can access this bucket.
* Creates an Elastic IP (eip) and Route53 domain for drone. Automatically updated during upgrades (not implemented yet).
* Sets up security group rules for http, https, and ssh access from the ip addresses you specify.

## Quickstart (semi-manual until app is completed)

Ultimately, we will use drone to deploy and manage updates to itself, but we need to bootstrap the initial server first.

### Bootstrap steps

1. Create a new [OAuth application for drone in githhub](https://github.com/settings/developers) in your github account settings.
2. Clone the repo and edit project settings.
3. Setup IAM roles and policies.
4. Build the drone server AMI.
5. Deploy drone.

#### 1. Create an OAuth application in github

Log into your GitHub account and visit https://github.com/settings/developers. From there, you can click on the `New OAuth App` button.

Required Field | Value
---------------|------
Application name | Drone
Homepage URL | https://drone.yourdomainname.com
Authorization callback URL | https://drone.yourdomainname.com/login

Then click 'Register application'

Once done, view the oath app and take note of the `Client ID` and `Client Secret`.

> *Note: it's important to make sure the callback url ends with '/login'*

#### 2. Clone the repo and edit project settings.

Clone the repo

```shell
git clone git@github.com:keithdadkins/drone.podchaser.com.git
cd drone.podchaser.com
```

Edit and source project settings

```shell
cp .env.example .env
vi .env
source .env
```

#### 3. Setup IAM Roles and Policies

> !! __IMPORTANT__ You cannot use an AWS root account when deploying this project. This is because a root account cannot call the AssumeRole api (you will get 'access is denied') and the scripts will fail. https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html#lock-away-credentials

```shell
cd terraform
terraform apply -target=aws_iam_policy.drone-builder-ec2 \
                -target=aws_iam_policy.drone-builder-s3 \
                -target=aws_iam_policy_attachment.ec2 \
                -target=aws_iam_policy_attachment.s3 \
                -target=aws_iam_instance_profile.drone-builder
cd ..
```

This will ensure the appropriate roles and permissions are created in AWS. Take note of the `DRONE_BUILDER_ROLE_ARN` output that was generated during the process:

```shell
...
Apply complete! Resources: 6 added, 0 changed, 0 destroyed.
DRONE_BUILDER_ROLE_ARN = arn:aws:iam::YOUR_ACCOUNT_NUMBER:role/drone-builder-role
```

Copy this and update the `export DRONE_BUILDER_ROLE_ARN=...` line in your `.env` file.

#### 4. Build the drone-server ami

Assuming you are using the default aws profile (not aws access keys) build the ami with the `-p` flag as follows. This will use your currently configured default aws profile (or whatever is set in the env var 'AWS_DEFAULT_PROFILE'):

```shell
# source the .env file to pickup the DRONE_BUILDER_ROLE_ARN change from the previous step.
. .env
./build-drone-server-ami.sh -p
```

This can take a few minutes to complete. When done, check the `packer/manifest.json` file for the following settings:

- "drone_deployment_id"
- "artifact_id"

These will contain the unique **'drone_deployment_id'** that is used to tag and authorize resources and the **'artifact_id'**.

