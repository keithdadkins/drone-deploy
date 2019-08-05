import os
from packaging import version
from cli import cli

def test_cli_smoke_test(runner):
    '''smoke test'''
    result = runner.invoke(cli)
    assert 'Usage:' in result.output, "'drone-deploy' did not contain Usage text."
    assert result.exit_code == 0, "'drone-deploy' returned a non-zero exit status."


def test_cli_version(runner):
    result = runner.invoke(cli, ["version"])
    assert version.parse(result.output) > version.parse("0.0.1"), 'drone-deploy version should return a valid version greater than 0.0.1'
