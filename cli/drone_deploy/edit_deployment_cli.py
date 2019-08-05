import os
import click
from pathlib import Path
from drone_deploy.filter import filter_deployments


# $> drone-deploy edit <deployment-name>
@click.group(invoke_without_command=True, name='edit')
@click.argument('deployment_name', type=click.STRING, autocompletion=filter_deployments)
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
