import os
import sys
import pytest
import shutil
import subprocess
from cli import cli
from pathlib import Path
from click.testing import CliRunner


@pytest.fixture()
def terraform_cmd():
    def terraform(command, working_dir, tf_targets=None, tf_args=None):
        if tf_targets:
            command = f"terraform {command} {tf_targets}"
        else:
            command = f"terraform {command}"

        if tf_args:
            command = f"{command} {tf_args}"

        # copy .terraform from test cache into working dir to prevent us from having
        # to 'terraform init' aws module, which would greatly slow down testing
        terra_cache = Path(os.getcwd()).parent.joinpath('cache', '.terraform')
        if terra_cache.exists():
            shutil.copytree(terra_cache, working_dir.joinpath('.terraform'))

        # pass our env vars along to the sub process when executed
        env = os.environ
        p = subprocess.Popen(command, stderr=subprocess.PIPE, shell=True, text=True,
                             cwd=working_dir, env=env)
        while True:
            out = p.stderr.read(1)
            if out == '' and p.poll() is not None:
                break
            if out != '':
                sys.stdout.write(out)
                sys.stdout.flush()
    return terraform


def setup_test_dir():
    # setup the test deployment directory (recreate if present)
    test_dir = Path.cwd().joinpath('cli', 'tests', 'test-deployments')
    if test_dir.exists():
        shutil.rmtree(test_dir)
    Path(test_dir).mkdir(exist_ok=False, parents=True)

    # copy templates to test dir
    from_template_path = Path.cwd().joinpath('templates')
    to_template_path = test_dir.joinpath('templates')

    shutil.copytree(from_template_path, to_template_path)
    return test_dir.resolve()


def teardown_test_dir(test_dir):
    if test_dir.exists():
        shutil.rmtree(test_dir)


@pytest.fixture(scope='session')
def new_deployment(runner):
    # create a new deployment 'foo'
    result = runner.invoke(cli, ["new", "foo"])
    return result


@pytest.fixture(scope='session')
def runner():
    # create, setup, and move to the test deployment directory
    test_dir = setup_test_dir()

    # change to the test directory for the duration of testing
    os.chdir(test_dir)
    runner = CliRunner()
    yield runner

    # teardown when down
    teardown_test_dir(test_dir)
