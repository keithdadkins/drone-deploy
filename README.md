[![Build Status](https://drone.keithdadkins.me/api/badges/keithdadkins/drone.podchaser.com/status.svg?ref=refs/heads/master)](https://drone.keithdadkins.me/keithdadkins/drone.podchaser.com)

# Drone

This projects builds, deploys, and maintains a [Drone.io](https://drone.io) CI/CD installation on AWS.

## Bootstrapping Drone (only needs to be done once)

Ultimately, we will use drone itself to deploy and manage updates to our drone installation; However, we must first manually bootstrap the initial drone ami and instance.

The basic steps for deploying drone the first time:

1. Create a new [oath application for drone in githhub](https://github.com/settings/developers)
2. Setup IAM roles, policies, and instance profiles.
3. Edit our drone configuration.
4. Build the drone server AMI.
5. Launch and configure the server. TODO: terraform

### 1. Create an OATH application in github

Log into your GitHub account and visit https://github.com/settings/developers. From there, you can click on the `New OAuth App` button.

Required Field | Value
---------------|------
Application name | Drone
Homepage URL | https://drone.yourdomainname.com
Authorization callback URL | https://drone.yourdomainname.com/login

Then click 'Register application'

Once done, view the oath app, take note of the `Client ID` and `Client Secret` and update the `DRONE_GITHUB_CLIENT_ID` and `DRONE_GITHUB_CLIENT_SECRET` settings in your .env file accordingly.

>  *Note: it's important to make sure the callback url ends with '/login'*

### 2. Setup IAM

>  !! __IMPORTANT__ You cannot call AssumeRole when using AWS root account credentials (you will get 'access is denied').

IAM Instance Profiles, Roles, and Policies

