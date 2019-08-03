import subprocess
from cli import cli
from pathlib import Path


def test_cli_destroy_deployment(runner, terraform_cmd, mocker):
    '''drone-deploy destroy'''
    # create a new deployment for testing
    result = runner.invoke(cli, ["new", "foobar"])
    assert result.exit_code == 0, "Error creating a 'foobar' deployment when testing 'destroy'."

    # test destroying resources
    mocker.patch('subprocess.Popen')
    runner.invoke(cli, ["destroy", "foobar"])
    call_list = f'{subprocess.Popen.call_args}'    # noqa
    assert 'terraform destroy' in call_list, "'drone-deploy destroy' did not call 'terraform destroy' as expected."
    assert 'TF_VAR_drone_github_server' in call_list, "Did not find an expected TF_VAR_ env var in a call to 'terraform destroy'"
    assert subprocess.Popen.call_count == 1, "'drone-deploy destroy' should only call 'terraform destroy' once."    # noqa


def test_cli_destroy_deployment_with_rm(runner, terraform_cmd, mocker):
    '''drone-deploy destroy --rm'''
    # create a new deployment for testing
    result = runner.invoke(cli, ["new", "foobar-rm"])
    assert result.exit_code == 0, "Error creating a 'foobar-rm' deployment when testing 'destroy'."

    foobar_path = Path.cwd().joinpath('deployments', 'foobar-rm').resolve()
    terraform_cmd('init', foobar_path)

    # # test destroying resources
    # mocker.patch('subprocess.Popen')
    # runner.invoke(cli, ["destroy", "foobar"])
    # call_list = f'{subprocess.Popen.call_args}'    # noqa
    # assert 'terraform destroy' in call_list, "'drone-deploy destroy' did not call 'terraform destroy' as expected."
    # assert 'TF_VAR_drone_github_server' in call_list, "Did not find an expected TF_VAR_ env var in a call to 'terraform destroy'"
    # assert subprocess.Popen.call_count == 1, "'drone-deploy destroy' should only call 'terraform destroy' once."    # noqa

    
    # verify it's on disk now & run 'destroy --rm foobar' to verify deletion from disk
    if foobar_path.exists():
        result = runner.invoke(cli, ["destroy", "--rm", "foobar-rm"])
        assert not foobar_path.exists(), 'Error when destroying with --rm. Did not delete from deployment from disk.'
    else:
        assert False, 'Error creating a deployment "foobar" when testing destroy.'


def test_cli_duplicate_deployments_not_allowed(runner):
    '''drone-deploy new foobar.acme.com'''
    runner.invoke(cli, ["new", "foobar.acme.com"])
    result = runner.invoke(cli, ["new", "foobar.acme.com"])
    assert 'Deployment with that name already exists.' in result.output, "Allowed duplicate deployment."
