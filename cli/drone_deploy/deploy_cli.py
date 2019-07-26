import click
from pathlib import Path
from drone_deploy.deployment import Deployment


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


# $> drone-deploy deploy [deployment name]
@click.group(invoke_without_command=True)
@click.argument('deployment_name', type=click.STRING, autocompletion=list_deployments)
@click.pass_obj
def deploy(aws, deployment_name):
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

    # # load the deployment
    deployment = Deployment(deployment_dir)
    click.echo(f"Deploying {deployment_name}...")
    deployment.deploy()
