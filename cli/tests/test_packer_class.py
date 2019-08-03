import os
import json
import pytest
import subprocess
from pathlib import Path, PosixPath, WindowsPath
from drone_deploy.deployment import Deployment


@pytest.fixture()
def deployment():
    config_file = Path.cwd().joinpath('deployments', 'foo', 'config.yaml').resolve()
    deployment = Deployment(config_file)
    return deployment


@pytest.fixture()
def valid_manifest_file():
    manifest_file = Path.cwd().joinpath('deployments', 'foo', 'packer', 'manifest.json')
    manifest = """\
{
  "builds": [
    {
      "name": "drone-server-ami",
      "builder_type": "amazon-ebs",
      "build_time": 1564347734,
      "files": null,
      "artifact_id": "us-east-1:ami-0edf58c4682eddea0",
      "packer_run_uuid": "adc2e76b-0ecd-465f-7cdf-4fbb61473a7d",
      "custom_data": {
        "builder_arn": "",
        "drone_deployment_id": "fb8b32847f4f9569d9094d966af7a0cb"
      }
    }
  ],
  "last_run_uuid": "adc2e76b-0ecd-465f-7cdf-4fbb61473a7d"
}"""

    with open(manifest_file, 'w') as outfile:
        outfile.write(manifest)

    yield manifest_file
    os.remove(manifest_file)


@pytest.fixture()
def invalid_manifest_file():
    manifest_file = Path.cwd().joinpath('deployments', 'foo', 'packer', 'manifest.json')
    manifest = "}garbilygook}"
    with open(manifest_file, 'w') as outfile:
        outfile.write(manifest)
    yield manifest_file
    os.remove(manifest_file)


def test_packer_vars(deployment, new_deployment):
    packer = deployment.packer
    assert len(packer.packer_vars) > 0, "packer_vars failed to populate as expected."
    assert '-var drone_server_instance_type=t2.micro' in packer.packer_vars, 'packer vars failed to populate as expected.'


def test_packer_working_dir(deployment, new_deployment):
    packer = deployment.packer
    assert type(packer.working_dir) in [PosixPath, WindowsPath], 'packer.working_dir is not a valid Posix or Windows path.'


def test_packer_loading_valid_manifest_file(deployment, valid_manifest_file, new_deployment):
    if valid_manifest_file.exists():
        packer = deployment.packer
        packer.load_artifacts()
        assert 'builds' in packer.manifest, "Could not find expected 'builds' key in manifest."
        assert packer.drone_server_ami == "ami-0edf58c4682eddea0", "Could not find expected drone_server_ami in manifest."
        assert packer.drone_deployment_id == "fb8b32847f4f9569d9094d966af7a0cb", "Could not find expected drone_deployment_id in manfiest."
        assert packer.new_build is False, "'packer.new_build' should be False if a valid manifest is presesnt."


def test_packer_with_invalid_manifest_file(deployment, new_deployment, invalid_manifest_file):
    if invalid_manifest_file.exists():
        packer = deployment.packer
        x = packer.load_artifacts()
        if type(x) is json.decoder.JSONDecodeError:
            assert True
        else:
            assert False, "Invalid manifest.json file should raise json.decoder.JSONDecodeError."


def test_packer_without_existing_manifest_file(deployment, new_deployment):
    packer = deployment.packer
    packer.load_artifacts()
    assert packer.new_build is True, "'packer.new_build' should be True if manifest.json file is not present."
    assert packer.drone_deployment_id == '', "'packer.drone_deployment_id' should be empty string if manifest file is not present."
    assert packer.drone_server_ami == '', "'packer.drone_server_ami' should be empty string if manifest file is not present."


def test_packer_build_ami_command_should_load_artifacts(deployment, new_deployment, mocker, valid_manifest_file):
    if valid_manifest_file.exists():
        packer = deployment.packer
        assert packer.drone_server_ami == '', 'Error setting up test case. packer.drone_server_ami should be empty string.'
        mocker.patch('subprocess.Popen')
        packer.build_ami()
        call_list = f'{subprocess.Popen.call_args}'    # noqa
        assert subprocess.Popen.call_count == 1, "packer.build_ami() should call build script once."
        assert './build-drone-server-ami.sh' in call_list, "packer.build_ami() did not call ./build-drone-server-ami.sh as expected."
        assert packer.drone_deployment_id == "fb8b32847f4f9569d9094d966af7a0cb", "packer did not load artifacts from manifest file after build as expected."
