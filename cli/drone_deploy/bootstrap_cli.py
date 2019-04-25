import os
import click
from drone_deploy.terraform import set_iam_roles_and_policies, apply
from drone_deploy.packer import build_ami

# $> drone-deploy bootstrap
@click.group(invoke_without_command=True)
@click.pass_obj
def bootstrap(aws):
    """
    Bootstrap process (set perms, build ami)
    """
    click.echo("Configuring IAM Roles and Policies... ")
    set_iam_roles_and_policies()

    click.echo("Building AMI... ")
    aws_profile = aws.profile_name
    build_ami(profile_name=aws_profile)

    # deploy
    ami_id = os.get
    apply()