import click
from pathlib import Path

# $> drone-deploy list
@click.group(invoke_without_command=True, name="list")
def list_deployments():
    """
    Lists deployments.
    """
    deployment_dir = Path.cwd().joinpath('deployments').resolve()
    for deployment in deployment_dir.glob("*"):
        if deployment.is_dir():
            click.echo(deployment.name)
