import os
import click
from pathlib import Path


def list_deployments(ctx, args, incomplete):
    """
    Display list of deployments for bash autocompletion
    """
    deployments = []
    try:
        deployment_dir = Path.cwd().joinpath('deployments').resolve()
        for deployment in deployment_dir.glob(f'{incomplete}*'):
            if deployment.is_dir():
                deployments.append(click.echo(deployment.name))
        return [k for k in deployments if incomplete in k]
    except Exception:
        return ""


# $> drone-deploy edit <deployment-name>
@click.group(invoke_without_command=True, name='edit')
@click.argument('deployment_name', type=click.STRING, autocompletion=list_deployments)
def edit_deployment(deployment_name):
    """
    Edits <deployment-name>'s config file with default $EDITOR.
    """
    config_file = Path.cwd().joinpath('deployments', deployment_name, 'config.yaml').resolve()
    if not config_file.exists():
        click.echo("Couldn't find the deployment."
                   "Run 'drone-deploy list' to see available deployemnts.")
        return False

    editor = os.getenv('EDITOR')
    if editor:
        os.system(f"{editor} {str(config_file)}")
    else:
        click.echo(f"No default EDITOR found to open:")
        click.echo(config_file)
