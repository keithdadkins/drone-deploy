import click
from pathlib import Path
from drone_deploy.deployment import Deployment

# $> drone-deploy show <deployment-name>
@click.group(invoke_without_command=True)
@click.argument('deployment_name')
def show(deployment_name):
    """
    Shows <deployment-name>'s configuration.
    """
    deployment_dir = Path.cwd().joinpath('deployments', deployment_name, 'config.yaml').resolve()
    if not deployment_dir.exists():
        click.echo("Couldn't find the deployment."
                   "Run 'drone-deploy list' to see available deployemnts.")
        return False

    # load the deployment
    deployment = Deployment(deployment_dir)
    click.echo(deployment)
