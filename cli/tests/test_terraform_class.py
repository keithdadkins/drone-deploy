import os
import pytest
from pathlib import Path, PosixPath, WindowsPath
from drone_deploy.deployment import Deployment
from drone_deploy.terraform import Terraform


@pytest.fixture()
def deployment():
    config_file = Path.cwd().joinpath('deployments', 'foo', 'config.yaml').resolve()
    deployment = Deployment(config_file)
    return deployment


@pytest.fixture()
def valid_tf_state_file():
    state_file = Path.cwd().joinpath('deployments', 'foo', 'terraform', 'terraform.tfstate')
    state = """\
{
    "version": 3,
    "terraform_version": "0.11.14",
    "serial": 2,
    "lineage": "68212074-5905-8b20-e769-6cc400e53eb1",
    "modules": [
        {
            "path": [
                "root"
            ],
            "outputs": {
                "DRONE_BUILDER_ROLE_ARN": {
                    "sensitive": false,
                    "type": "string",
                    "value": "arn:aws:iam::1234567890:role/drone.foo.com-builder"
                }
            },
            "resources": {
            },
            "depends_on": []
        }
    ]
}"""
    with open(state_file, 'w') as outfile:
        outfile.write(state)

    yield state_file
    os.remove(state_file)


@pytest.fixture()
def invalid_tf_state_file():
    state_file = Path.cwd().joinpath('deployments', 'foo', 'terraform', 'terraform.tfstate')
    state = "}garbilygook}"
    with open(state_file, 'w') as outfile:
        outfile.write(state)
    yield state_file
    os.remove(state_file)


def test_tf_vars(deployment, new_deployment):
    tf = deployment.terraform
    assert len(tf.tf_vars) > 0, "tf_vars failed to populate as expected."
    assert 'drone_server_instance_type' in tf.tf_vars, 'tf_vars failed to populate as expected.'


def test_working_dir(deployment, new_deployment):
    tf = deployment.terraform
    assert type(tf.working_dir) in [PosixPath, WindowsPath], 'terraform.working_dir is not a valid Posix or Windows path.'


def test_tf_state_is_false_with_new_deployment(deployment, new_deployment):
    tf = deployment.terraform
    assert tf.has_tf_state is False, 'terraform.tf_state should be false with a new deployment.'


def test_loading_valid_tf_state_file(deployment, valid_tf_state_file, new_deployment):
    if valid_tf_state_file.exists():
        tf = deployment.terraform
        tf.load_tf_state()
        assert tf.has_tf_state is True, 'Unable to load valid tf state file.'


def test_loading_invalid_tf_state_file(deployment, invalid_tf_state_file, new_deployment):
    if invalid_tf_state_file.exists():
        tf = deployment.terraform
        tf.load_tf_state()
        assert tf.has_tf_state is False, 'Was able to load an invalid tfstate file.'


def test_loading_role_arn_from_tfstate_file(deployment, valid_tf_state_file, new_deployment):
    if valid_tf_state_file.exists():
        tf = deployment.terraform
        tf.load_tf_state()
        assert "arn:aws:iam::1234567890:role/drone.foo.com-builder" in tf.drone_builder_role_arn, 'Was unable to load the correct IAM role arn from tf_state file.'


def test_terraform_wrapper_commands_present(mocker):
    config_file = Path.cwd().joinpath('deployments', 'foo', 'config.yaml').resolve()
    mocker.patch('drone_deploy.terraform.Terraform.init')
    mocker.patch('drone_deploy.terraform.Terraform.plan')
    mocker.patch('drone_deploy.terraform.Terraform.apply')
    mocker.patch('drone_deploy.terraform.Terraform.destroy')
    terraform = Terraform(config_file.parent)
    terraform.init()
    terraform.plan(tf_targets=['-target=aws_iam_policy.drone-builder-ec1'])
    terraform.apply(tf_targets=['-target=aws_iam_policy.drone-builder-ec2'])
    terraform.destroy(tf_targets=['-target=aws_iam_policy.drone-builder-ec3'])
    terraform.init.assert_called_once
    terraform.plan.assert_called_once_with(tf_targets=['-target=aws_iam_policy.drone-builder-ec1'])
    terraform.apply.assert_called_once_with(tf_targets=['-target=aws_iam_policy.drone-builder-ec2'])
    terraform.destroy.assert_called_once_with(tf_targets=['-target=aws_iam_policy.drone-builder-ec3'])
