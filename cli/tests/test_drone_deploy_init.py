import os
import shutil
import pytest
import drone_deploy
from cli import cli
from pathlib import Path, PosixPath
from click.testing import CliRunner
from drone_deploy.init_cli import setup_templates as cli_setup_templates, \
                                  copy_file_from_templates

@pytest.fixture()
def init_runner():
    old_dir = Path.cwd()
    test_dir = Path.cwd().joinpath('test-init-deployments')
    if test_dir.exists():
        shutil.rmtree(test_dir)
    Path(test_dir).mkdir(exist_ok=False, parents=True)
    os.chdir(test_dir)
    runner = CliRunner()
    yield runner
    os.chdir(old_dir)
    shutil.rmtree(test_dir)


def test_cli_init_with_default_path():
    # Running default init from within the existing repo could possibly destroy real 
    # deployment data, so we are testing the individual methods manually instead
    pass


def test_cli_init_with_full_path(init_runner):
    drone_deployments = Path.cwd().joinpath('foo-drones')
    assert drone_deployments.exists() is False, f'Failed to setup directories for testing.'

    # run init
    path_str = f"{str(drone_deployments.resolve())}"
    result = init_runner.invoke(cli, ["init", path_str])
    assert result.exit_code == 0, f"'drone-deploy init {path_str}' exited with a non-zero status."

    # check folders
    folders = ['deployments', 'templates']
    for folder in folders:
        if drone_deployments.joinpath(folder).exists():
            assert True
        else:
            assert False, f"'drone-deploy init {path_str}' failed to create {folder}."


def test_cli_init_with_relative_path(init_runner):
    drone_deployments = Path.cwd().joinpath('relative-foos')
    assert drone_deployments.exists() is False, f'Failed to setup directories for testing.'

    # run init with relative path
    result = init_runner.invoke(cli, ["init", "relative-foos"])
    assert result.exit_code == 0, "'drone-deploy init relative-foos' exited with a non-zero status."

    # check folders
    folders = ['deployments', 'templates']
    for folder in folders:
        if drone_deployments.joinpath(folder).exists():
            assert True
        else:
            assert False, f"'drone-deploy init relative-foos' failed to create {folder}."


def test_cli_init_with_cwd(init_runner):
    new_dir = Path.cwd().joinpath('new-dir')
    assert new_dir.exists() is False, f'Failed to setup directories for testing.'

    # make the new directory
    Path(new_dir).mkdir(exist_ok=False, parents=True)
    os.chdir(new_dir)

    # run init on .
    result = init_runner.invoke(cli, ["init", "."])
    assert result.exit_code == 0, "'drone-deploy init .' exited with a non-zero status."
     # check folders
    folders = ['deployments', 'templates']
    for folder in folders:
        if new_dir.joinpath(folder).exists():
            assert True
        else:
            assert False, f"'drone-deploy init .' failed to create {folder}."



def test_cli_init_does_not_overwrite_data(init_runner):
    drone_deployments = Path.cwd().joinpath('foos-drones2')
    assert drone_deployments.exists() is False, f'Failed to setup directories for testing.'

    # run init
    result = init_runner.invoke(cli, ["init", 'foos-drones2'])
    assert result.exit_code == 0, f"'drone-deploy init foos-drones2' exited with a non-zero status."

    # check folders
    folders = ['deployments', 'templates']
    for folder in folders:
        if drone_deployments.joinpath(folder).exists():
            assert True
        else:
            assert False, f"'drone-deploy init foos-drones2' failed to create {folder}."

    # try again (testing deployments folder)
    result = init_runner.invoke(cli, ["init", 'foos-drones2'])
    assert 'deployments\' would be destroyed' in result.output, "'drone-deploy init foos-drones2' may destroy deployments."
    assert drone_deployments.joinpath('deployments').exists() is True, 'drone-deploy destroyed existing deployemts directory.'
    
    # try again (testing templates)
    shutil.rmtree(drone_deployments.joinpath('deployments'))
    result = init_runner.invoke(cli, ["init", 'foos-drones2'])
    assert 'templates\' would be destroyed' in result.output, "'drone-deploy init foos-drones2' may destroy templates."
    assert drone_deployments.joinpath('templates').exists() is True, 'drone-deploy destroyed existing templates directory.'

    # ensure we are skipping files if they exist
    shutil.rmtree(drone_deployments.joinpath('deployments'))
    shutil.rmtree(drone_deployments.joinpath('templates'))
    result = init_runner.invoke(cli, ["init", 'foos-drones2'])
    assert '.gitignore\' already exists.. ignoring' in result.output, 'drone-deploy init did not skip .gitignore'
    assert True


def test_setup_templates_from_src(mocker):
    # setup mocks and test directory
    mocker.patch('shutil.copytree')
    mocker.patch('drone_deploy.init_cli.copy_templates_from_repo')
    test_dir = Path.cwd().joinpath('setup-templates-test')
    cli_setup_templates(test_dir)

    # make sure we tried to call copytree correctly
    assert shutil.copytree.called is True, 'failed copying templates from source'
    call_args_src = shutil.copytree.call_args_list[0][0][0]
    call_args_dest = shutil.copytree.call_args_list[0][0][1]
    
    # check source and dest
    assert type(call_args_src) and type(call_args_dest) is PosixPath, '"setup_templates" was called with invalid PosixPath'
    src = str(call_args_src).split('/')
    dest = str(call_args_dest).split('/')
    assert src[-1] == 'templates' and dest[-1] == 'setup-templates-test', 'setup_templates did not copy using expected source and destination'
    
    # make sure we didn't call copy_templates_from_repo
    assert drone_deploy.init_cli.copy_templates_from_repo.called is False, 'setup_templates tried to copy from repo'


def test_setup_templates_from_repo(mocker):
    # TODO
    pass
