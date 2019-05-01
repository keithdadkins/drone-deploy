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
2. Clone the repo, create a new deployment, and edit the config.yaml.
3. Prepare the deployment (sets up IAM roles and policies).
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

#### 2. Clone the repo, create new deployment, and edit config.yaml.

Clone the repo and setup the cli for your operating system.

```shell
git clone git@github.com:keithdadkins/drone.podchaser.com.git
cd drone.podchaser.com
make
```

Create a new project

```shell
./drone-deploy new drone.yourdomain.com
```

Edit config.yaml

You will need the following information:

- The aws region and vpc id of the vpc you want to deploy drone into
- The route53 hosted zone and machine name for drone (e.g., drone.yourdomain.com)
- An ec2 key-pair to use to ssh into the drone server (either existing or create new ones)
- Your public ip address (to allow ssh connections)
- The github username of the drone admin
- The github organization or github username(s) of each person you want to allow access to drone.


```shell
cp .env.example .env
vi .env
source .env
./drone-deploy edit drone.yourdomain.com
```

You can view the current state of the deployments config file by:

```shell
./drone-deploy show drone.yourdomain.com
```

#### 3. Prepare the deployment (sets up IAM roles and policies).

> !! __IMPORTANT__ You cannot use an AWS root account when deploying this project. This is because a root account cannot call the AssumeRole api (you will get 'access is denied') and the scripts will fail. https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html#lock-away-credentials

To bootstrap the deployment

```shell
./drone-deploy prepare drone.yourdomain.com
```

This sets up the IAM roles and policies to enable us to build and launch the drone-server ami.

#### 4. Build the drone-server ami

```shell
./drone-deploy build-ami drone.yourdomain.com
```

This can take a few minutes to complete and it's best to allow it to finish (don't ctl+c unless absolutely needed).

#### 5. Deploy

```shell
./drone-deploy deploy drone.yourdomain.com
```

This step only takes a sec to finish, but it could take a few minutes before the server is up and running.

```shell
ssh -i ~/.ssh/your_key_pair.pem ubuntu@drone.yourdomain.com
```

You can also setup a shortcut in `~/.ssh/config`

```shell
Host "drone.yourdomain.com"
	HostName "drone.yourdomain.com"
	User ubuntu
	IdentityFile ~/.ssh/your-key-pair.pem
```
