import click
from pathlib import Path
from drone_deploy.deployment import Deployment
from drone_deploy.filter import filter_deployments


# $> drone-deploy prepare [deployment name]
@click.group(invoke_without_command=True, name="prepare")
@click.argument('deployment_name', type=click.STRING, autocompletion=filter_deployments)
def prepare_deployment(deployment_name):
    """
    Sets up and prepares the deployment. Specifically, it runs 'terraform init'
    on <deployment_name> and bootstraps the needed IAM roles and policies for
    building and launching the AMI ec2 instance.

    This command can be run at any time, and will update/upgrade terraform aws
    components if needed. But, it must be run at least once for each deployment.

    The <deployment-name> must exist in the ./deployments directory.

    Usage:
        $> drone-deploy new drone.mydomain.com
        # edit deployments/drone.mydomain.com/config.yaml
        $> drone-deploy prepare drone.mydomain.com

    Related:
        drone-deploy [list, show, deploy]
    """

    deployment_dir = Path.cwd().joinpath('deployments', deployment_name, 'config.yaml').resolve()
    if not deployment_dir.exists():
        click.echo("Couldn't find the deployment."
                   "Run 'drone-deploy list' to see available deployemnts.")
        return False

    # load the deployment, run terraform init, and apply roles and policies
    deployment = Deployment(deployment_dir)
    try:
        deployment.init()
    except Exception:
        pass

    # Apply needed IAM roles and policies for building/deploying ami
    targets = ' '.join("-target={}".format(t) for t in [
        "aws_iam_policy.drone-builder-ec2",
        "aws_iam_policy.drone-builder-s3",
        "aws_iam_policy_attachment.ec2",
        "aws_iam_policy_attachment.s3",
        "aws_iam_instance_profile.drone-builder"
    ])

    deployment.deploy(targets)
