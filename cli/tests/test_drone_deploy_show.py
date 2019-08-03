from cli import cli


def test_cli_show(runner, new_deployment):
    '''drone-deploy show'''
    result = runner.invoke(cli, ["show", "foo"])
    assert 'DEPLOYMENT CONFIG FILE' in result.output, "'drone-deploy show foo' failed after a new deployment."


def test_cli_showing_unknown_deployment_should_error(runner):
    result = runner.invoke(cli, ["show", "foobarrrr"])
    assert "Couldn't find the deployment. Run 'drone-deploy list' to see available deployemnts." in result.output
