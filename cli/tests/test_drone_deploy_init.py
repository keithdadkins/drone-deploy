from cli import cli


def test_cli_init_with_default_path(runner, deployments_dir):
    '''drone-deploy init [path]'''
    default_dir = deployments_dir.joinpath('acme-deployments')
    result = runner.invoke(cli, ["init", default_dir])
    assert result.exit_code == 0, "Failed running 'drone-deploy init' with no args."
    assert default_dir.exists() is False, f'Test setup failed. {default_dir} already exists.'
    if default_dir.exists():
        assert True
    else:
        assert False, "'drone-deploy init' with no args did not create a new 'deployments' dir as expected."

    # templates directory
    if default_dir.joinpath('templates').exist():
        assert True
    else:
        assert False, "'drone-deploy init' failed to copy the templates folder from github"
