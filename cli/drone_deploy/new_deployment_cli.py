import click
import shutil
from pathlib import Path


def create_deployment_dir_if_not_exists(name):
    '''Returns a path to the deployment directory. Creates directory if needed'''
    try:
        deployment_path = Path.cwd().joinpath('deployments', name)
        Path(deployment_path).mkdir(exist_ok=False, parents=True)
    except FileExistsError:
        return False
    # return the full path
    return deployment_path.resolve()


def copy_terraform_to(deployment_dir):
    '''copy terraform templates to new deployment folder'''
    # copy each .tf file
    terra_path = Path.cwd().joinpath('templates','terraform')
    for file in terra_path.glob('*.tf'):
        shutil.copy(file, deployment_dir)


def generate_config_yaml(deployment_dir):
    '''creates an empty config.yaml file in the deployments folder'''
    template_file = Path('templates/config.yaml')
    shutil.copy(template_file, deployment_dir)

# $> drone-deploy new
@click.group(invoke_without_command=True)
@click.argument('name')
@click.pass_obj
def new(aws, name):
    """
    Creates a new deployment configuration in the 'deployments' directory.

    Usage:
        `drone-deploy new NAME`

    Where NAME == a friendly name for your deployment.

    Example:
        `drone-deploy new drone.yourdomain.com`
    """
    # create the deployment/$name directory
    deployment_dir = create_deployment_dir_if_not_exists(name)
    if not deployment_dir:
        click.echo("Deployment with that name already exists.")
        return False

    # copy our configs and generate the config.yaml file
    copy_terraform_to(deployment_dir)
    generate_config_yaml(deployment_dir)
