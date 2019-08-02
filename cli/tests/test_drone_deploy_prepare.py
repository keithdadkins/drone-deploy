import subprocess
from cli import cli


def test_cli_prepare(runner, new_deployment, mocker):
    '''test that drone-deploy prepare runs terraform init and iam related terraform apply'''
    mocker.patch('subprocess.Popen')
    runner.invoke(cli, ["prepare", "foo"])
    call_list = f'{subprocess.Popen.call_args}'    # noqa
    iam_targets = ["-target=aws_iam_policy.drone-builder-ec2",
                   "-target=aws_iam_policy.drone-builder-s3",
                   "-target=aws_iam_policy_attachment.ec2",
                   "-target=aws_iam_policy_attachment.s3",
                   "-target=aws_iam_instance_profile.drone-builder"]
    for t in iam_targets:
        assert t in call_list, f"'drone-deploy prepare' did not apply {t} as expected."
    assert 'terraform apply' in call_list and 'foo/terraform' in call_list, "'drone-deploy prepare' did not call 'terraform apply' as expected."
    assert subprocess.Popen.call_count == 2, "'drone-deploy prepare' should call 'terraform init' and 'terraform apply' once each."    # noqa
