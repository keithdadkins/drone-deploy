import click
import shutil
from pathlib import Path


def create_deployment_dir_if_not_exists(name):
    '''Returns a path to the deployment directory. Creates directories as needed'''
    try:
        deployment_path = Path.cwd().joinpath('deployments', name)
        terraform_path = deployment_path.joinpath('terraform')
        # packer_path = deployment_path.joinpath('packer')
        Path(terraform_path).mkdir(exist_ok=False, parents=True)
        # Path(packer_path).mkdir(exist_ok=False, parents=True)
    except FileExistsError:
        return False
    # return the path to the deploymen
    return deployment_path.resolve()


def copy_packer_templates_to(deployment_dir):
    '''copy packer templates to deployment dir'''
    template_path = Path.cwd().joinpath('templates', 'packer')
    deployment_path = deployment_dir.joinpath('packer')
    shutil.copytree(template_path, deployment_path)

    # copy the ami build script to the deployment directory
    build_script = Path.cwd().joinpath('build-drone-server-ami.sh').resolve()
    shutil.copy(build_script, deployment_dir)


def copy_terraform_templates_to(deployment_dir):
    '''copy terraform templates to new deployment folder'''
    # copies /templates/terraform/*.tf* to /deployments/foo/terraform/
    template_path = Path.cwd().joinpath('templates', 'terraform')
    deployment_path = deployment_dir.joinpath('terraform')
    for file in template_path.glob('*.tf*'):
        shutil.copy(file, deployment_path)


def generate_config_yaml(deployment_dir):
    '''creates an empty config.yaml file in the deployments folder'''
    template_file = Path('templates/config.yaml')
    shutil.copy(template_file, deployment_dir)

# $> drone-deploy new
@click.group(invoke_without_command=True, name="new")
@click.argument('name')
def new_deployment(name):
    """
    Creates a new deployment in the /deployments directory.

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
    copy_terraform_templates_to(deployment_dir)
    copy_packer_templates_to(deployment_dir)
    generate_config_yaml(deployment_dir)

    click.echo(f"Deployment created: {deployment_dir}")
    click.echo("Next steps:")
    click.echo(f"  - edit the config.yaml file ('drone-deploy edit {name}')")
    click.echo(f"  - run 'drone-deploy prepare {name}' to bootstrap the deployment.")
    click.echo(f"  - run 'drone-deploy build-ami {name} to build the drone-server ami.")
    click.echo(f"  - run 'drone-deploy plan|apply {name} to deploy.")
