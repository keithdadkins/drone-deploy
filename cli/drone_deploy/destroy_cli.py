import click
import shutil
from pathlib import Path
from drone_deploy.deployment import Deployment
from drone_deploy.filter import filter_deployments


@click.group(invoke_without_command=True)
@click.argument('deployment_name', type=click.STRING, autocompletion=filter_deployments)
@click.option('--rm/--no-rm', default=False)
def destroy(deployment_name, rm):
    """
    !!! Destroys (runs 'terraform destroy') on <deployment_name> resources.

    The <deployment-name> must exist in the ./deployments directory.

    Usage:
        drone-deploy destroy drone.mydomain.com

        Tears down any aws resources created during deploy. The S3 data bucket must
        be emptied and deleted manually.

    """

    deployment_dir = Path.cwd().joinpath('deployments', deployment_name, 'config.yaml').resolve()
    if not deployment_dir.exists():
        click.echo("Couldn't find the deployment."
                   "Run 'drone-deploy list' to see available deployemnts.")
        return False

    # # load the deployment
    deployment = Deployment(deployment_dir)
    click.echo(f"Destroying {deployment_name}...")
    deployment.destroy()

    if rm:
        # delete the directory
        shutil.rmtree(deployment_dir.parent)
