from click.testing import CliRunner
from cli import cli


def test_cli_smoke_test():
    '''smoke test'''
    runner = CliRunner()
    result = runner.invoke(cli)
    assert result.exit_code == 0, "'drone-deploy' returned a non-zero exit status"


def test_cli_with_named_profile():
    runner = CliRunner()
    result = runner.invoke(cli, ["--profile=default", "config", "list-available-profiles"])
    assert 'default' in result.output, "could not use named profile 'default'"


def test_cli_fails_with_invalid_profile():
    runner = CliRunner()
    result = runner.invoke(cli, ["--profile='foooobarrrsss'", "config", "list-available-profiles"])
    assert 'default' not in result.output, "should not be able to use an invalid --profile name"
