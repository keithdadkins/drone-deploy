import subprocess
from cli import cli


def test_cli_deploy(runner, new_deployment, mocker):
    '''drone-deploy deploy'''
    mocker.patch('subprocess.Popen')
    runner.invoke(cli, ["deploy", "foo"])
    call_list = f'{subprocess.Popen.call_args}'    # noqa
    assert 'terraform apply' in call_list, "'drone-deploy deploy' did not call 'terraform apply' as expected."
    assert 'TF_VAR_drone_github_server' in call_list, "Did not find an expected TF_VAR_ env var in a call to 'terraform apply'"
    assert subprocess.Popen.call_count == 1, "'drone-deploy deploy' should only call 'terraform apply' once."    # noqa
