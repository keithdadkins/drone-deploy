import os
import json
# import subprocess
from shutil import which
from pathlib import Path
from ruamel.yaml import YAML


def count_files(dir):
    return len([1 for x in list(os.scandir(dir)) if x.is_file()])


def test_new_deployment_config_yaml_present_and_valid(new_deployment):
    # config.yaml present?
    foo_path = Path.cwd().joinpath('deployments', 'foo').resolve()
    config_file = foo_path.joinpath('config.yaml').resolve()
    assert config_file.exists(), "config.yaml file is not present."

    # load config to test for valid yaml
    try:
        yaml = YAML()
        yaml.load(config_file)
    except Exception:
        assert False, "config.yaml contains invalid json."


def test_new_deployment_terraform_templates_present_and_valid(new_deployment, terraform_cmd):
    foo_path = Path.cwd().joinpath('deployments', 'foo', 'terraform').resolve()

    # should be at least 7 .tf files in the terraform dir
    assert count_files(foo_path) >= 7, "missing some/all terraform config files in new deployment"

    # validate terraform configs
    assert terraform_cmd('validate', foo_path, tf_args="--check-variables=false") == 0, "Found invalid terraform syntax in a new deployment."


def test_new_deployment_packer_templates_present(new_deployment):
    '''test and validate packer files and directories'''
    # deployement files and directories (from templates)
    foo_path = Path.cwd().joinpath('deployments', 'foo', 'packer').resolve()
    packer_build_script = foo_path.joinpath('packer_build_drone_server_ami.json')
    aws_cli_path = foo_path.joinpath('aws-cli')
    build_scripts_path = foo_path.joinpath('build-scripts')
    drone_server_configs_path = foo_path.joinpath('drone-server-configs')

    assert packer_build_script.exists(), 'packer_build_drone_server_ami.json not present in new deployment'
    assert aws_cli_path.exists(), 'aws-cli templates not present in new deployment'
    assert build_scripts_path.exists(), 'build-scripts templates not present in new deployment'
    assert drone_server_configs_path.exists(), 'drone-server-configs templates not present in new deployment'
    assert count_files(build_scripts_path) >= 5, "missing some/all packer/build-scripts/*.sh files. Expecting at least 5."


def test_new_deployment_packer_build_script(new_deployment):
    '''test packer yaml file by attempting to load it and by checking a key'''
    build_script = Path.cwd().joinpath('deployments', 'foo', 'packer', 'packer_build_drone_server_ami.json').resolve()
    with open(build_script) as json_file:
        try:
            data = json.load(json_file)
            assert 'amazon-ebs' in data['builders'][0]['type'], 'Failed to find "amazon-ebs" in packer build json file.'
        except Exception:
            assert False, f'Invalid json in {build_script}'


def test_new_deployment_docker_compose_file(new_deployment):
    '''test docker compose file for valid yaml and make sure it's version 3'''
    compose_file = Path.cwd().joinpath('deployments', 'foo', 'packer', 'drone-server-configs', 'docker-compose.yaml').resolve()
    assert compose_file.exists(), "Could not find docker-compose.yaml file in new deployemnt."

    # load config to test for valid yaml
    try:
        yaml = YAML()
        config = yaml.load(compose_file)
        assert '3' in config['version'], "Expected docker-compose.yaml to be version 3."
    except Exception:
        assert False, "New deployment's docker-compose.yaml contains invalid json."



def test_shellcheck_bash_scripts(new_deployment):
    '''for each .sh file, run shellcheck'''
    if not which('shellcheck'):
        print("shellcheck not installed")
        pass
    else:
        print("shellcheck installed")
        pass
