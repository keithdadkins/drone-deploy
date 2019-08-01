import subprocess
from cli import cli
from pathlib import Path


def test_cli_plan(runner, new_deployment, mocker):
    '''drone-deploy plan'''
    mocker.patch('subprocess.Popen')
    runner.invoke(cli, ["plan", "foo"])
    call_list = f'{subprocess.Popen.call_args}'    # noqa
    assert subprocess.Popen.call_count == 1, "'drone-deploy plan' should only call 'terraform plan' once."    # noqa
    assert 'terraform plan' in call_list, "'drone-deploy plan' did not call 'terraform plan' as expected."
    assert 'TF_VAR_drone_github_server' in call_list, 'Did not find an expected TF_VAR_ env var in a call to terraform plan.'
