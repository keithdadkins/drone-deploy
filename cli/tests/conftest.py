import pytest
import shutil
from cli import cli
from pathlib import Path
from click.testing import CliRunner


def setup_test_deployments():
    # setup the test deployment directory (recreate if present)
    test_dir = Path.cwd().joinpath('tests', 'test-deployments')
    if test_dir.exists():
        shutil.rmtree(test_dir)
    Path(test_dir).mkdir(exist_ok=False, parents=True)
    return test_dir.resolve()


def teardown_test_deployments(test_dir):
    if test_dir.exists():
        shutil.rmtree(test_dir)


@pytest.fixture(scope='session')
def runner():
    # create, setup, and move to the test deployment directory
    test_dir = setup_test_deployments()
    runner = CliRunner()
    # runner.invoke(cli, ["new", "drone.acme.com"])
    yield runner
    # teardown when down
    teardown_test_deployments(test_dir)
    # runner.invoke(cli, ["destroy", "--rm", "drone.acme.com"])
