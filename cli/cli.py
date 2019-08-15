import os
import sys
import click
from version import __version__
from pathlib import Path
from dotenv import load_dotenv
from drone_deploy import new_deployment, prepare_deployment,\
                         list_deployments, show, plan, deploy,\
                         edit_deployment, build_ami, destroy,\
                         show_agent_command, init_dir


# $> drone-deploy
@click.group()
@click.pass_context
def cli(ctx):
    """
    Deploys and manages Drone CI/CD deployments on AWS.
    """
    pass

@cli.command()
def version():
    """
    drone-deploy version (SemVer)
    """
    click.echo(click.style(f'{__version__}', bold=True))


def setup():
    # make sure we are in project root
    # check_dir()

    # load env vars from .env file. They will be available, along with any other
    # env vars, by using os.getenv("ENV_VAR_NAME") in the project
    env_path = Path(__file__).parent.joinpath('.env')
    load_dotenv(dotenv_path=env_path)

    # hookup 'drone-deploy' sub commands
    # cli.add_command(bootstrap)
    cli.add_command(new_deployment)
    cli.add_command(edit_deployment)
    cli.add_command(prepare_deployment)
    cli.add_command(build_ami)
    cli.add_command(list_deployments)
    cli.add_command(show)
    cli.add_command(plan)
    cli.add_command(deploy)
    cli.add_command(destroy)
    cli.add_command(show_agent_command)
    cli.add_command(init_dir)

setup()
