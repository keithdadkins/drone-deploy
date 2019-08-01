from cli import cli
from pathlib import Path
from drone_deploy.deployment import Deployment
from drone_deploy.deployment import Terraform


def test_destroy_deployment(runner, terraform_cmd, mocker):
    '''drone-deploy destroy'''
    # create a new deployment for testing
    result = runner.invoke(cli, ["new", "foobar"])
    assert result.exit_code == 0, "Error creating a 'foobar' deployment when testing 'destroy'."

    # init terraform for the tests
    foobar_path = Path.cwd().joinpath('deployments', 'foobar').resolve()
    terraform_cmd('init', foobar_path)

    # test destroying resources TODO: need to mock this somehow. For now, just check for any
    # response back from terraform to verify that the command at least ran.
    result = runner.invoke(cli, ["destroy", "foobar"])
    assert 'Destroying foobar' in result.output, "Unable to destroy a new deployment."

    # verify it's on disk now & run 'destroy --rm foobar' to verify deletion from disk
    if foobar_path.exists():
        runner.invoke(cli, ["destroy", "--rm", "foobar"])
        assert not foobar_path.exists(), 'Error when destroying with --rm. Did not delete from disk.'
    else:
        assert False, 'Error creating a deployment "foobar" when testing destroy.'


def test_duplicate_deployments_not_allowed(runner):
    '''drone-deploy new foobar.acme.com'''
    runner.invoke(cli, ["new", "foobar.acme.com"])
    result = runner.invoke(cli, ["new", "foobar.acme.com"])
    assert 'Deployment with that name already exists.' in result.output, "Allowed duplicate deployment."
