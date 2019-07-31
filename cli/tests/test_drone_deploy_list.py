from cli import cli


def test_cli_list(new_deployment):
    '''drone-deploy list'''
    # result = runner.invoke(cli, ["list"])
    assert new_deployment.exit_code == 0, "Error running 'drone-deploy list'"
    assert 'foo' in new_deployment.output, "'drone-deploy list' did not contain a deployment 'drone.acme.com.'"
