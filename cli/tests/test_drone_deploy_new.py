from cli import cli


def test_new_deployment(runner):
    '''drone-deploy new'''
    result = runner.invoke(cli, ["new", "drone.acme.com"])
    assert 'Deployment created:' in result.output, "Unable to create a new deployment."


def test_duplicate_deployments_not_allowed(runner):
    '''drone-deploy new foobar.acme.com'''
    runner.invoke(cli, ["new", "foobar.acme.com"])
    result = runner.invoke(cli, ["new", "foobar.acme.com"])
    assert 'Deployment with that name already exists.' in result.output, "Allowed duplicate deployment."
