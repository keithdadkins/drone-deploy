from cli import cli


def test_cli_list(runner, new_deployment):
    '''drone-deploy list'''
    result = runner.invoke(cli, ["list"])
    assert result.exit_code == 0, "Error running 'drone-deploy list'"
    assert 'foo' in new_deployment.output, "'drone-deploy list' did not contain the expected new_deployment."
