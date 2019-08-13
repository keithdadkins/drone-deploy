# `drone-deploy` User Guide

> ** __WIP__ **

## Quickstart

1. Create a new [OAuth application for drone in githhub](https://github.com/settings/developers) in your github account settings. (see below)

2. Clone the repo 

    ```shell 
    git clone https://github.com/keithdadkins/drone-deploy.git
    cd drone-deploy
    ```

3. Either download `drone-deploy` from git releases and add to your $PATH, or build it manually:

    ```shell
    make virtualenv         # installs python virtualenv if you don't have it
    make venv               # creates a virtual environment for the project
    make test && make       # test and build the cli
    . cli/venv/bin/activate # source the environment (type `deactivate` when done or close your shell)
    # run the following for bash completion
    eval "$(_DRONE_DEPLOY_COMPLETE=source drone-deploy)"
    ```

4. Create a new deployment and edit the settings

   ```shell
   drone-deploy new drone.yourdomain.com
   drone-deploy edit drone.yourdomain.com # uses your default editor to edit
   ```

5. Build the AMI
   ```shell
   drone-deploy prepare drone.yourdomain.com # this sets up the necessary IAM permissions
   drone-deploy build-ami drone.yourdomain.com
   ```


6. Deploy drone.
   ```shell
   drone-deploy deploy drone.yourdomain.com
   ```


## 1. Create an OAuth application in github

Log into your GitHub account and visit https://github.com/settings/developers. From there, you can click on the `New OAuth App` button.

Required Field | Value
---------------|------
Application name | Drone
Homepage URL | https://drone.yourdomainname.com
Authorization callback URL | https://drone.yourdomainname.com/login

Then click 'Register application'

Once done, view the oath app and take note of the `Client ID` and `Client Secret`.

> *Note: it's important to make sure the callback url ends with '/login'*


## Detailed Setup (WIP)

### Clone the repo, create new deployment, and edit config.yaml.

Clone the repo and setup the cli for your operating system.

```shell
git clone git@github.com:keithdadkins/drone-deploy.git
cd drone-deploy
make venv # setups up a virtualenv in the cli directory
make # installs requirements and sets up the cli in the path
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

#### Prepare the deployment (sets up IAM roles and policies).

> !! __IMPORTANT__ You cannot use an AWS root account when deploying this project. This is because a root account cannot call the AssumeRole api (you will get 'access is denied') and the scripts will fail. https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html#lock-away-credentials

To bootstrap the deployment

```shell
./drone-deploy prepare drone.yourdomain.com
```

This sets up the IAM roles and policies to enable us to build and launch the drone-server ami.

#### Build the drone-server ami

```shell
./drone-deploy build-ami drone.yourdomain.com
```

This can take a few minutes to complete and it's best to allow it to finish (don't ctl+c unless absolutely needed).

#### Deploy

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
 
