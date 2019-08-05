import click
from pathlib import Path
from drone_deploy.deployment import Deployment
from drone_deploy.filter import filter_deployments


# $> drone-deploy deploy [deployment name]
@click.group(invoke_without_command=True)
@click.argument('deployment_name', type=click.STRING, autocompletion=filter_deployments)
def deploy(deployment_name):
    """
    Deploys (runs 'terraform apply') on <deployment_name> resources.

    The <deployment-name> must exist in the ./deployments directory.

    Usage:
        drone-deploy deploy drone.mydomain.com

    Related:
        drone-deploy [new, prepare, list, show, plan]
    """

    deployment_dir = Path.cwd().joinpath('deployments', deployment_name, 'config.yaml').resolve()
    if not deployment_dir.exists():
        click.echo("Couldn't find the deployment."
                   "Run 'drone-deploy list' to see available deployemnts.")
        return False

    # load the deployment
    deployment = Deployment(deployment_dir)
    click.echo(f"Deploying {deployment_name}...")
    deployment.deploy()
