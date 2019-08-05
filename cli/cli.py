import os
import sys
import click
import boto3
import boto3.session
import botocore.exceptions
from version import __version__
from pathlib import Path
from dotenv import load_dotenv
from drone_deploy import new_deployment, prepare_deployment,\
                         list_deployments, show, plan, deploy,\
                         edit_deployment, build_ami, destroy,\
                         show_agent_command


def check_dir():
    '''ensure we are running in project root'''
    if not Path('templates').exists():
        click.echo("drone-deploy must be run from the project root directoy.")
        sys.exit("Exiting.")


def aws_session(aws_access_key_id=None, aws_secret_access_key=None, aws_session_token=None,
                profile_name=None):
    '''
    Returns a boto3 session we can pass around using click's context object. This is the session
    that the app and api uses to communicate with AWS. Notes:
        - Uses access keys over profile if available.
        - Uses callers region if region_name is not set.
    '''
    session = boto3.session.Session()

    # try to get a session using aws access keys first
    if aws_access_key_id or aws_access_key_id:
        try:
            session = boto3.session.Session(aws_access_key_id, aws_secret_access_key,
                                            aws_session_token)
        except Exception as e:
            print(type(e))
            print(e.args)
            print(e)
            sys.exit("Exiting.")
        return session

    # else try using a profile
    else:
        try:
            session = boto3.session.Session(profile_name=profile_name)
        except botocore.exceptions.ProfileNotFound as err:
            print(str(err), file=sys.stderr)
            if session.available_profiles:
                print(f"'{profile_name}' was not found. Verify the profile name or try with"
                      "one of the following available profiles: {session.available_profiles}",
                      file=sys.stderr)
        except Exception as e:
            print(type(e))
            print(e.args)
            print(e)
            sys.exit("Exiting.")
        return session


# $> drone-deploy
@click.group()
@click.option('--region', '-r', help="The AWS region for the drone deployment.")
@click.pass_context
def cli(ctx, region):
    """
    Deploys and manages Drone CI/CD deployments on AWS.

    AWS access keys or profiles can be used; however one or the other must be configured and
    an aws region must set in order to make requests.
    """

    # load aws creds from env vars if available
    profile = os.getenv("AWS_DEFAULT_PROFILE", "default")
    aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    aws_session_token = os.getenv("AWS_SESSION_TOKEN")
    if region is None:
        region = os.getenv("DRONE_REGION", os.getenv('AWS_REGION'))

    # create an aws session and set it's region. We will pass this around the cli app
    # in the 'ctx' context object.
    if ctx.obj is None:
        ctx.obj = dict()

    ctx.obj['aws'] = aws_session(profile_name=profile,
                                 aws_access_key_id=aws_access_key_id,
                                 aws_secret_access_key=aws_secret_access_key,
                                 aws_session_token=aws_session_token)
    ctx.obj['aws'].region = region


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


setup()
