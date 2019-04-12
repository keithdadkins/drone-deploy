# podchaser-drone-ami-builder

This projects builds and deploys https://drone.podchaser.com CI/CD system using Drone.io

## Requirements to run locally

> - [packer](https://www.packer.io) - IaC tool used to build the drone server AWS AMI
> - [terraform](https://www.terraform.io) - IaC tool used to deploy and manage AWS resources

## The podchaser-drone-server Server AMI

The server AMI is built ontop of Ubuntu 18.04LTS. We use `packer` to install and provision:

- Ubuntu 18.04 LTS (installs OS updates during builds)
- docker-ce
- docker-compose
- drone command line tools

Before a build, decide which region you want the ami to reside in and [get the latest Ubuntu AMI (18.04LTS) ami id from Ubuntu's EC2 locator](https://cloud-images.ubuntu.com/locator/ec2/) for that region. This is the `base_ami` id that we install drone and docker ontop of.

You can manually update build defaults by editing the `variables` section in the `podchaser_drone_server_ami.json` build file, and/or overide them by setting the vars from the cli (e.g., `packer -var region=us-west-1 ...`.

For example, you want to deploy Drone version 1.0.7 and you used Ubuntu's ami locator above and found that the latest Ubuntu 18.04LTS AMI id is `ami-0fba9b33b5304d8b4` for the `us-east-1` region. You also check https://hub.docker.com/r/drone/drone/tags to find the appropriate drone image to use (they do now always sync 1:1). To build the AMI you would run:

```bash
cd packer
packer build \
    -var region=us-east-1 \
    -var base_ami=ami-0fba9b33b5304d8b4 \
    -var drone_version="1.0.7" \
    -var drone_image="drone/drone:1"
    podchaser_drone_server_ami.json
```

The build will take a few minutes to complete, but at the end you should see output similar to the following:

```bash
...
==> podchaser-drone-server: Creating AMI tags
    podchaser-drone-server: Adding tag: "ami": "podchaser-drone-server"
==> podchaser-drone-server: Creating snapshot tags
==> podchaser-drone-server: Terminating the source AWS instance...
==> podchaser-drone-server: Cleaning up any extra volumes...
==> podchaser-drone-server: No volumes to clean up, skipping
==> podchaser-drone-server: Deleting temporary security group...
==> podchaser-drone-server: Deleting temporary keypair...
Build 'podchaser-drone-server' finished.

==> Builds finished. The artifacts of successful builds are:
--> podchaser-drone-server: AMIs were created:
us-east-1: ami-0c7831ef22e8dc86d
```

At the bottom of the output, you should see a line like: `us-east-1: ami-0c7831ef22e8dc86d`. This is the AMI we will use to deploy new drone instances from. This AMI contains all the current OS updates along with docker, drone, etc.

## Initial Deployment

> !WIP

Terraform will handle provisioning all the necessary resources for `drone.podchaser.com` including: s3, route53, load balancers, etc.

TODO

## Updates

> !WIP

After the drone server is deployed, keeping the OS patched and updated is a straightforward process:

TODO

* Drone's build logs, configs, and sqlite db data is persisted in either the EBS volume we created during the intial deployment, or in an s3 bucket, so it's safe to rebuild and redeploy the server.


## TODO

- [ ] Install specific docker-ce version

