import os
import boto3
from packaging import version
from cli import cli, aws_session


def test_cli_smoke_test(runner):
    '''smoke test'''
    result = runner.invoke(cli)
    assert 'Usage:' in result.output, "'drone-deploy' did not contain Usage text."
    assert result.exit_code == 0, "'drone-deploy' returned a non-zero exit status."


def test_cli_version(runner):
    result = runner.invoke(cli, ["version"])
    assert version.parse(result.output) > version.parse("0.0.1"), 'drone-deploy version should return a valid version greater than 0.0.1'


def test_aws_session_ctx(runner):
    '''test aws session'''
    os.environ["AWS_SESSION"] = 'us-east-5'
    aws_access_key_id = '1234567890'
    aws_secret_access_key = 'ABCDE1234567890'
    aws = aws_session(aws_access_key_id=aws_access_key_id,
                      aws_secret_access_key=aws_secret_access_key,
                      aws_session_token='')
    assert type(aws) is boto3.session.Session, 'aws'
