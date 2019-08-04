import os
from cli import cli


def test_cli_edit(runner, new_deployment, mocker):
    '''drone-deploy show'''
    os.environ["EDITOR"] = "vim"
    mocker.patch('os.system')
    runner.invoke(cli, ["edit", "foo"])
    call_list = f'{os.system.call_args}'    # noqa
    assert 'config.yaml' in call_list, 'drone-deploy edit did not attempt to open config.yaml file with an editor.'
    assert os.system.call_count == 1, 'drone-deploy edit should only make one syscall to edit config.yaml' # noqa
