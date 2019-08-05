import click
from pathlib import Path
from drone_deploy.deployment import Deployment
from drone_deploy.filter import filter_deployments


# $> drone-deploy show-agent-command <deployment-name>
@click.group(invoke_without_command=True)
@click.argument('deployment_name', type=click.STRING, autocompletion=filter_deployments)
def show_agent_command(deployment_name):
    """
    Shows the docker command used to launch agents for a deployment.
    """
    deployment_dir = Path.cwd().joinpath('deployments', deployment_name, 'config.yaml').resolve()
    if not deployment_dir.exists():
        click.echo("Couldn't find the deployment."
                   "Run 'drone-deploy list' to see available deployemnts.")
        return False

    # display the docker command to run an agent
    deployment = Deployment(deployment_dir)
    rpc_secret = deployment.config['drone_rpc_secret']
    agent_image = deployment.config['drone_agent_docker_image']

    docker_command = f'''
        # Run the following command on a host running docker to launch a build agent:

        docker run -v /var/run/docker.sock:/var/run/docker.sock \\
            -e DRONE_RPC_SERVER=https://{deployment_name} \\
            -e DRONE_RUNNER_CAPACITY=1 \\
            -e DRONE_RPC_SECRET={rpc_secret} \\
            -d {agent_image}
    '''
    click.echo(docker_command)
