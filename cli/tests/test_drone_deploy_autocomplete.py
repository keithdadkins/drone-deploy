import sys
import drone_deploy.deploy_cli
from io import StringIO


def test_cli_autocompletion(runner, new_deployment, new_deployment2):
    autocomp_clis = [
        "deploy_cli",
        "build_ami_cli",
        "destroy_cli",
        "edit_deployment_cli",
        "plan_cli",
        "prepare_deployment_cli",
        "show_agent_command_cli",
        "show_cli"
    ]

    for autocomp_cli in autocomp_clis:
        dc = eval(f'drone_deploy.{autocomp_cli}')

        filters = ["", "f", "ba"]
        for filter in filters:
            # capture stdout
            old_stdout = sys.stdout
            sys.stdout = result = StringIO()
            dc.filter_deployments(ctx=[], args=[], incomplete=filter)
            deploys = result.getvalue().split("\n")
            sys.stdout = old_stdout

            # account for an extra blank new line in result count
            if filter == '':
                assert len(deploys) >= 3, 'Should be at least two deployment in autocomplete list.'
            elif filter == 'f':
                assert len(deploys) == 2, 'Should only be one deployment in autocomplete list.'
                assert 'foo' in deploys, 'Expected `foo` to be in autocomplete list when filtering for `f`'
            elif filter == 'ba':
                assert len(deploys) == 2, 'Should only be one deployment in autocomplete list.'
                assert 'bar' in deploys, 'Expected `bar` to be in autocomplete list when filtering for `ba`'
