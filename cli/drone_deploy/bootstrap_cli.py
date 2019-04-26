import os
import sys
import click
from drone_deploy.terraform import set_iam_roles_and_policies, apply
from drone_deploy.packer import build_ami

# $> drone-deploy bootstrap
@click.group(invoke_without_command=True)
@click.pass_obj
def bootstrap(aws):
    """
    Bootstraps a server.
    """
    if aws.region is None:
        print("The AWS 'region' must be set to make requests.", file=sys.stderr)
        sys.exit("Exiting.")

    click.echo("Configuring IAM Roles and Policies... ")
    set_iam_roles_and_policies()

    click.echo("Building AMI... ")
    aws_profile = aws.profile_name
    build_ami(profile_name=aws_profile)

    # deploy
    ami_id = os.get
    apply()
