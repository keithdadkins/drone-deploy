from click.testing import CliRunner
from cli import cli


def test_cli_smoke_test():
    '''smoke test'''
    runner = CliRunner()
    result = runner.invoke(cli)
    assert result.exit_code == 0, "'drone-deploy' returned a non-zero exit status"


def test_config_list_deployments():
    '''drone-deploy list'''
    # TODO setup deployment for testing
    runner = CliRunner()
    result = runner.invoke(cli, ["list"])
    assert 'foobar' in result.output, "could not list deployments"
