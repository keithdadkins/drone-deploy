from cli import cli


def test_cli_list(runner):
    '''drone-deploy list'''
    result = runner.invoke(cli, ["list"])
    assert 'drone.acme.com' in result.output, "'drone-deploy list' did not contain a deployment 'drone.acme.com.'"
