import click
from pathlib import Path
from drone_deploy.deployment import Deployment

# $> drone-deploy build-ami
@click.group(invoke_without_command=True)
@click.argument('deployment_name')
def build_ami(deployment_name):
    """
    Builds the drone server AMI (Amazon Machine Image).
    """
    deployment_dir = Path.cwd().joinpath('deployments', deployment_name)
    if not deployment_dir.exists():
        click.echo("Couldn't find the deployment."
                   "Run 'drone-deploy list' to see available deployemnts.")
        return False

    # # load the deployment
    deployment = Deployment(deployment_dir.joinpath('config.yaml').resolve())
    deployment.build_ami()
