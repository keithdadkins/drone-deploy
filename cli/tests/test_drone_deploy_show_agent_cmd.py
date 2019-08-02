from cli import cli


def test_cli_show_agent_command(runner, new_deployment):
    '''drone-deploy show'''
    result = runner.invoke(cli, ["show-agent-command", "foo"])
    # breakpoint()
    assert result.exit_code == 0, "'drone-deploy show-agent-command' returned a non zero exit status."
    assert 'docker run' in result.output, "'drone-deploy show-agent-command' failed to display expected text."
    assert 'DRONE_RPC_SERVER' in result.output, "'drone-deploy show-agent-command' failed to display expected text."
    assert 'DRONE_RPC_SECRET' in result.output, "'drone-deploy show-agent-command' failed to display expected text."
