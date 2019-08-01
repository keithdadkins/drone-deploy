import subprocess
from cli import cli


def test_cli_build_ami(runner, new_deployment, mocker):
    '''drone-deploy build-ami'''
    mocker.patch('subprocess.Popen')
    runner.invoke(cli, ["build-ami", "foo"])
    call_list = f'{subprocess.Popen.call_args}'    # noqa
    assert './build-drone-server-ami.sh' in call_list, "'drone-deploy build-ami' did not call ./build-drone-server-ami.sh as expected."
    assert 'TF_VAR_drone_github_server' in call_list, 'Did not find an expected TF_VAR_ env var in a call to ./build-drone-server-ami.sh'
    assert subprocess.Popen.call_count == 1, "'drone-deploy build-ami' should only call build script once."    # noqa