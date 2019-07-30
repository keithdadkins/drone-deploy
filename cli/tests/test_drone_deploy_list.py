from cli import cli


def test_cli_list(runner):
    '''drone-deploy list'''
    result = runner.invoke(cli, ["list"])
    assert 'foo' in result.output, "'drone-deploy' did not contain Usage text."
