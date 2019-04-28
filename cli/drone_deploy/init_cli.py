import click
from pathlib import Path
from drone_deploy.deployment import Deployment

# $> drone-deploy init [deployment name]
@click.group(invoke_without_command=True, name="init")
@click.argument('deployment_name')
def init_terraform(deployment_name):
    """
    Runs 'terraform init' on <deployment_name>. This is automatically run during
    'drone-deploy new <deployment_name>', but can be run again to update/upgrade
    terraform aws components. It is required for terraform to work correctly.

    The <deployment-name> must exist in the ./deployments directory.

    Usage:
        drone-deploy new drone.mydomain.com # runs init
        # or
        drone-deploy init drone.mydomain.com # runs init again, possibly upgrading

    Related:
        drone-deploy [list, show, deploy]
    """

    deployment_dir = Path.cwd().joinpath('deployments', deployment_name, 'config.yaml').resolve()
    if not deployment_dir.exists():
        click.echo("Couldn't find the deployment."
                   "Run 'drone-deploy list' to see available deployemnts.")
        return False

    # load the deployment and init.
    deployment = Deployment(deployment_dir)
    deployment.init()
