import os
from pathlib import Path
from ruamel.yaml import YAML


def count_files(dir):
    return len([1 for x in list(os.scandir(dir)) if x.is_file()])


def test_config_yaml_present_and_valid(new_deployment):
    # config.yaml present?
    foo_path = Path.cwd().joinpath('deployments', 'foo').resolve()
    config_file = foo_path.joinpath('config.yaml').resolve()
    assert config_file.exists(), "config.yaml file is not present."

    # load config to test for valid yaml
    try:
        yaml = YAML()
        config = yaml.load(config_file)
    except Exception:
        assert False, "config.yaml contains invalid json."

    # check a few keys for default values
    assert 'your_github_user_name' in config['drone_admin'], "a new config.yaml did not contain default value for github username (your_github_user_name)"
    assert 'https' in config['drone_server_proto'], "a new config.yaml did not contain default value for drone_server_proto (https)"


def test_terraform_templates_present_and_valid(new_deployment, terraform_cmd):
    foo_path = Path.cwd().joinpath('deployments', 'foo', 'terraform').resolve()

    # should be at least 7 files in the terraform dir
    assert count_files(foo_path) >= 7, "missing some/all terraform config files in new deployment"

    # validate terraform configs
    # assert terraform_cmd('validate', foo_path), "Found invalid terraform syntax in new deployment."
    pass


def test_packer_templates_present_and_valid(new_deployment):
    # aws-cli
    # build-scripts
    # drone-server-configs
    # packer build script
    pass


def test_shellcheck_bash_scripts(new_deployment):
    '''for each .sh file, run shellcheck'''
    # TODO
    pass
