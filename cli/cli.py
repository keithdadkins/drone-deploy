import sys
import click
import boto3
import boto3.session
import botocore.exceptions
from pathlib import Path
from dotenv import load_dotenv
from drone_deploy import new_deployment, bootstrap, list_deployments


def check_dir():
    '''ensure we are running in project root'''
    if not Path('terraform').exists() or not Path('drone-deploy').exists():
        click.echo("drone-deploy must be run from the project root directoy.")
        sys.exit("Exiting.")


def aws_session(aws_access_key_id=None, aws_secret_access_key=None, aws_session_token=None,
                region_name=None, profile_name=None):
    """
    Returns a boto3 session we can pass around using click's context object. This is the session
    that the app and api uses to communicate with AWS. Notes:
        - Uses access keys over profile if available.
        - Uses callers region if region_name is not set.
    """
    session = boto3.session.Session()

    # try to get a session using aws profile
    if None not in (aws_access_key_id, aws_access_key_id, aws_session_token):
        try:
            session = boto3.session.Session(profile_name=profile_name, region_name=region_name)
        except botocore.exceptions.ProfileNotFound as err:
            print(str(err), file=sys.stderr)
            if session.available_profiles:
                print(f"'{profile_name}' was not found. Verify the profile name or try with"
                      "one of the following found profiles: {session.available_profiles}",
                      file=sys.stderr)
            else:
                print("No profiles found. You must run 'aws configure' before using profiles.",
                      file=sys.stderr)
                sys.exit("Exiting.")
        except Exception as e:
            print(type(e))
            print(e.args)
            print(e)
            sys.exit("Exiting.")

    # else try using access keys
    else:
        try:
            session = boto3.session.Session(aws_access_key_id, aws_secret_access_key,
                                            aws_session_token)
        except Exception as e:
            print(type(e))
            print(e.args)
            print(e)
            sys.exit("Exiting.")

    # check/set region
    if region_name:
        session.region_name = region_name
    else:
        if session.region_name is None:
            print("The AWS 'region' must be set to make requests.", file=sys.stderr)
            sys.exit("Exiting.")

    return session


# $> drone-deploy
@click.group()
@click.option('--profile', '-p', help="The name of an AWS profile to use.")
@click.option('--region', '-r', help="The AWS region for the drone deployment.")
@click.option('--aws-access-key-id')
@click.option('--aws-secret-access-key')
@click.option('--aws-session-token')
@click.pass_context
def cli(ctx, profile, region, aws_access_key_id, aws_secret_access_key, aws_session_token):
    """
    Deploys and manages Drone CI/CD deployments on AWS.

    AWS access keys or profiles can be used; however one or the other must be configured and
    an aws region must set in order to make requests.
    """

    # aws session to pass around
    ctx.obj = aws_session(profile_name=profile, region_name=region,
                          aws_access_key_id=aws_access_key_id,
                          aws_secret_access_key=aws_secret_access_key,
                          aws_session_token=aws_session_token)


# make sure we are in project root
check_dir()

# load .env file
env_path = Path(__file__).parent.joinpath('.env')
load_dotenv(dotenv_path=env_path)

# pyinstaller statement to make it work with click
if getattr(sys, 'frozen', False):
    cli(sys.argv[1:])


# hookup 'drone-deploy' sub commands
cli.add_command(bootstrap)
cli.add_command(new_deployment)
cli.add_command(list_deployments)
