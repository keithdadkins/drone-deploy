import sys
import click
from pathlib import Path
from drone_deploy.deployment import Deployment

# from drone_deploy.terraform import set_iam_roles_and_policies, apply
# from drone_deploy.packer import build_ami

# $> drone-deploy deploy [deployment name]
@click.group(invoke_without_command=True)
@click.argument('deployment_name')
@click.pass_obj
def deploy(aws, deployment_name):
    """
    Deploys <deployment-name> using Terraform. Deployment commands are just
    convienience methods: they are the same as changing into the deployments
    directory and running 'terraform plan', 'terraform apply' etc. The only
    difference is that if you do not have terraform installed, this app will
    run the commands using the 'terraform' docker image.

    The <deployment-name> must exist in the ./deployments directory.

    Usage:
        drone-deploy deploy drone.mydomain.com

    Related:
        drone-deploy [list, show]
    """
    if aws.region is None:
        print("The AWS 'region' must be set before deployment..", file=sys.stderr)
        sys.exit("Exiting.")

    deployment_dir = Path.cwd().joinpath('deployments', deployment_name, 'config.yaml').resolve()
    if not deployment_dir.exists():
        click.echo("Couldn't find the deployment."
                   "Run 'drone-deploy list' to see available deployemnts.")
        return False

    # load the deployment
    deployment = Deployment(deployment_dir)

    # apply
    click.echo(f"Deploying {deployment_name}")

    # try:
    #     deployment.plan()
    #     deployment.apply()

