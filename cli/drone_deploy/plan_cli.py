import click
from pathlib import Path
from drone_deploy.deployment import Deployment
from drone_deploy.filter import filter_deployments


# $> drone-deploy plan [deployment name]
@click.group(invoke_without_command=True)
@click.argument('deployment_name', type=click.STRING, autocompletion=filter_deployments)
def plan(deployment_name):
    """
    Runs 'terraform plan' on <deployment_name>.

    The <deployment-name> must exist in the ./deployments directory.

    Usage:
        drone-deploy plan drone.mydomain.com

    Related:
        drone-deploy [list, show, deploy]
    """

    deployment_dir = Path.cwd().joinpath('deployments', deployment_name, 'config.yaml').resolve()
    if not deployment_dir.exists():
        click.echo("Couldn't find the deployment."
                   "Run 'drone-deploy list' to see available deployemnts.")
        return False

    # load the deployment
    deployment = Deployment(deployment_dir)
    deployment.plan()
