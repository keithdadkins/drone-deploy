import os
import pytest
import ruamel
import drone_deploy
from ruamel.yaml import YAML
from drone_deploy.deployment import Deployment
from pathlib import Path


@pytest.fixture()
def deployment():
    config_file = Path.cwd().joinpath('deployments', 'foo', 'config.yaml').resolve()
    deployment = Deployment(config_file)
    return deployment


@pytest.fixture()
def valid_config_file():
    valid_path = Path.cwd().joinpath('deployments', 'valid-foo')
    os.makedirs(valid_path, exist_ok=True)
    config_file = valid_path.joinpath('config.yaml')
    config = """\
drone_aws_region:
drone_vpc_id:
drone_server_docker_image: drone/drone:1
drone_agent_docker_image: drone/agent:1
drone_cli_version: 1.0.8
drone_server_machine_name:
drone_server_hosted_zone:
drone_server_key_pair_name: drone-server
drone_server_instance_type: t2.micro
drone_docker_compose_version: 1.24.0
drone_server_allow_http:
- 0.0.0.0/0
drone_server_allow_https:
- 0.0.0.0/0
drone_server_allow_ssh:
- your.admins.ip.address/32
drone_open: false
drone_user_filter:
- your_github_user_name
- github_user_name_2
drone_admin: your_github_user_name
drone_admin_email: youremailaddy@yourdomain.com
drone_github_server: https://github.com
drone_github_client_id:
drone_github_client_secret:
drone_agents_enabled: true
drone_server_proto: https
drone_server_host: https://yourdroneserver
drone_rpc_secret:
drone_server_ami:
drone_deployment_id:
drone_deployment_name:
drone_builder_role_arn:
drone_s3_bucket:
"""
    with open(config_file, 'w') as outfile:
        outfile.write(config)

    yield config_file
    os.remove(config_file)


@pytest.fixture()
def invalid_config_file():
    invalid_path = Path.cwd().joinpath('deployments', 'invalid-foo')
    os.makedirs(invalid_path, exist_ok=True)
    config_file = invalid_path.joinpath('config.yaml')
    config = "}gibberjabber}}"
    with open(config_file, 'w') as outfile:
        outfile.write(config)
    yield config_file
    os.remove(config_file)


def test_deployment_with_valid_config_file(new_deployment):
    # default config.yaml present?
    foo_path = Path.cwd().joinpath('deployments', 'foo').resolve()
    config_file = foo_path.joinpath('config.yaml').resolve()
    assert config_file.exists(), "config.yaml file is not present."

    # load config to test for valid yaml
    try:
        yaml = YAML()
        config = yaml.load(config_file)
    except Exception:
        assert False, "config.yaml contains invalid yaml."

    # check a few keys for default values
    assert 'your_github_user_name' in config['drone_admin'], "config.yaml did not contain default value for github username (your_github_user_name)"
    assert 'https' in config['drone_server_proto'], "config.yaml did not contain default value for drone_server_proto (https)"


def test_deployment_with_invalid_config_file(invalid_config_file):
    if invalid_config_file.exists():
        try:
            Deployment(invalid_config_file)
            assert False, 'Was able to parse an invalid config.yaml file.'
        except ruamel.yaml.parser.ParserError:
            assert True


def test_deployment_class_deployment_with_missing_config_file():
    no_config = Path.cwd().joinpath('deployments', 'config.yaml')
    assert not no_config.exists(), "test error. deployments/config.yaml should not exist."
    try:
        Deployment(no_config)
        assert False, 'Did not raise FileNotFoundError as expected.'
    except FileNotFoundError:
        assert True


def test_deployment_class_loading_params_from_env(new_deployment):
    os.environ["DRONE_AWS_REGION"] = "us-east-5"
    config_file = Path.cwd().joinpath('deployments', 'foo', 'config.yaml').resolve()
    deployment = Deployment(config_file)
    assert deployment.config.get('drone_aws_region') == 'us-east-5', 'Param was not loaded from env vars as expected.'


def test_deployment_class_loading_params_from_config(deployment, new_deployment):
    # drone_server_proto is set to https in config.yaml by default
    assert deployment.config.get('drone_server_proto') == 'https', 'An expected param was not loaded from config.yaml.'


def test_deployment_class_writing_config_file_to_disk(new_deployment):
    os.environ["DRONE_AWS_REGION"] = "us-east-6"
    config_file = Path.cwd().joinpath('deployments', 'foo', 'config.yaml').resolve()
    deployment = Deployment(config_file)

    # update a param and write to disk
    assert deployment.config.get('drone_aws_region') == 'us-east-6', 'test setup failed. Param was not loaded from env vars as expected.'
    deployment.write_config()

    # verify
    yaml = YAML()
    config = yaml.load(config_file)
    assert 'us-east-6' in config['drone_aws_region'], "write_config() did not update param as expected."


def test_deployment_class_deployment__init__(deployment, new_deployment):
    assert type(deployment.config) is ruamel.yaml.comments.CommentedMap, '__init__ should have loaded and parsed the config.yaml'


def test_deployment_class_drone_deployment_name(deployment, new_deployment):
    assert 'drone-foo' in deployment.config.get('drone_deployment_name'), "drone_deployment_name should have dynamically been named 'drone-foo'"


def test_deployment_class_terraform_setup(deployment, new_deployment):
    assert type(deployment.terraform) is drone_deploy.terraform.Terraform, 'deployment.terraform was not instantiated.'


def test_deployment_class_packer_setup(deployment, new_deployment):
    assert type(deployment.packer) is drone_deploy.packer.Packer, 'deployment.packer was not instantiated.'


def test_deployment_class_str_repr(deployment, new_deployment):
    result = str(deployment)
    assert 'DEPLOYMENT' in result, 'Printing a deployment object should pretty print the deployments config.'


def test_deployment_class_generate_rpc(deployment, new_deployment):
    # generate_rpc(self, num_bytes=16):
    r16 = deployment.generate_rpc()
    r8 = deployment.generate_rpc(8)
    assert len(r16) == 32, 'generate_rpc() should generate 32 random characters by default.'
    assert len(r8) == 16, 'generate_rpc(8) should generate 16 random characters.'

    # test randomness by generating a few thousand rpcs
    test_cache = []
    for i in range(1, 5000):
        rpc = deployment.generate_rpc()
        assert rpc not in test_cache, 'generate_rpc() should generate random numbers.'
        test_cache.append(rpc)


def test_deployment_class_deployment_status(deployment, new_deployment):
    assert 'AMI has not been built' in deployment.deployment_status and \
           'drone-foo has not been deployed' in deployment.deployment_status, 'deployment_status not displaying expected text.'


def test_deployment_class_terraform_commands(deployment, new_deployment, mocker):
    mocker.patch('drone_deploy.terraform.Terraform.init')
    mocker.patch('drone_deploy.terraform.Terraform.plan')
    mocker.patch('drone_deploy.terraform.Terraform.apply')
    mocker.patch('drone_deploy.terraform.Terraform.destroy')
    deployment.init()
    deployment.plan()
    deployment.deploy(targets=["foo", "bar"])
    deployment.destroy()
    terraform = deployment.terraform
    terraform.init.assert_called_once
    terraform.plan.assert_called_once
    terraform.apply.assert_called_once_with(["foo", "bar"])


def test_deployment_class_packer_commands(deployment, new_deployment, mocker):
    mocker.patch('drone_deploy.packer.Packer.build_ami')
    deployment.build_ami()
    packer = deployment.packer
    packer.build_ami.assert_called_once
