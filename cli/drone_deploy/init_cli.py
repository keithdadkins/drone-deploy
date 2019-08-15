import os
import click
from pathlib import Path


def setup_deployments(path):
    print("setting up", path)


def setup_templates(path):
    print("setting up", path)


def setup_readme(path):
    print("setting up", path)


def setup_gitignore(path):
    print("setting up", path)


def setup_init_item(item, path):
    items = {
        'deployments': setup_deployments,
        'templates': setup_templates,
        'README.txt': setup_readme,
        '.gitignore': setup_gitignore
    }
    switcher = items.get(item)
    switcher(path)


@click.group(invoke_without_command=True, name="init")
@click.argument('path', type=click.Path(file_okay=False, writable=True),
                default=Path(os.getcwd()).joinpath('drone-deployments'))
def init_dir(path):
    """
    Initializes a new or existing 'deployments' working-directory by
    downloading templates, creating appropriate directories, etc.

    This is the first command that should be run before creating new
    deployments as 'drone-deploy' expects to be run from inside an initialized
    directory. Ideally, this directory should be managed by git or similar
    as it will contain deployment specific configs, terraform state, etc.

    This command is safe to run multiple times and will not overwrite data;
    However, the command will fail and you will receive errors if you
    attempt to run `init` on any directory that would result in overwriting
    existing data. If this is intentional, you will first need to `destroy`
    and/or delete any offending files/folders beforehand.

    If no arguments are given, then a folder named 'drone-deployments' will
    be created inside the current working directory and initialized.

    \b
    E.g., `drone-deploy init ~/my-drones` would create the 'my-drones' directory
    (if needed), and would create the following structure:
        ~/my-drones/templates   # pulls from github (do not rename)
        ~/my-drones/deployments # your deployments will be here (do not rename)
        ~/my-drones/.gitignore  # optional and can be edited/deleted
        ~/my-drones/README.txt  # optional and can be edited/deleted
    \b
    Usage:
        `drone-deploy init [<path>]`
    \b
    Examples:
        `drone-deploy init`             # creates a 'drone-deployments' folder     
        `drone-deploy init .`           # initializes the current working directory
        `drone-deploy init ~/my-drones` # creates and inits 'my-drones' in your home folder
    """
    # resolve the deployment path (tilde's are expanded before now so resolve any symlinks, etc.)
    base_path = Path(path).resolve()
    folders = ['deployments', 'templates']
    files = ['.gitignore', 'README.txt']

    # stop init if any of the folders exist, else create them
    for folder in folders:
        folder_path = base_path.joinpath(folder).resolve()
        if folder_path.exists():
            click.echo(click.style(f"stopping init because '{folder_path}' would be destroyed.",
                                   fg='red'))
            click.pause()
            ctx = click.get_current_context()
            click.echo(ctx.get_help())
            ctx.exit()
        else:
            # create the folder(s)
            setup_init_item(folder, folder_path)

    # ignore the files if present, else create them
    for file in files:
        file_path = base_path.joinpath(file).resolve()
        if file_path.exists():
            click.echo(click.style(f"'{file_path}' already exists.. ignoring", fg='yellow'))
        else:
            setup_init_item(file, file_path)
