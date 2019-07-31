from cli import cli


def test_cli_smoke_test(runner):
    '''smoke test'''
    result = runner.invoke(cli)
    assert 'Usage:' in result.output, "'drone-deploy' did not contain Usage text."
    assert result.exit_code == 0, "'drone-deploy' returned a non-zero exit status."
