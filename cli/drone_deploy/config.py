import click

# $> drone-deploy config
@click.group()
@click.pass_obj
def config(aws):
    """
    Drone deployment configuration commands.
    """
    pass


# $> drone-deploy config list_aws_profiles
@config.command()
@click.pass_obj
def list_available_profiles(aws):
    """
    List available AWS profiles.
    """
    click.echo(f"{aws.available_profiles}")
