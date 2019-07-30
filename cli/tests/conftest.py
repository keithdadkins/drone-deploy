import pytest
from click.testing import CliRunner


@pytest.fixture(scope='session')
def runner():
    runner = CliRunner()
    return runner
