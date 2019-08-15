import os
import sys
import click
import shutil
import version
import zipfile
import requests
import tempfile
from pathlib import Path


def setup_deployments(path):
    Path(path).mkdir(exist_ok=False, parents=True)
    if path.exists():
        click.echo(f"\tcreated '{path}'")
    else:
        click.echo(click.style(f"\t'failed setting up the deployments directory'", fg='red'))


def copy_templates_from_repo(path):
    Path(path).mkdir(exist_ok=False, parents=True)
    if path.exists():
        click.echo(f"\tcreated '{path}'.")
    else:
        click.echo(click.style(f"\tfailed setting up the templates directory", fg='red'))

    # pull templates from source (use a default repo unless overwritten via env vars)
    # e.g. https://github.com/keithdadkins/drone-deploy/archive/0.1.16.zip
    # the zip_base_path var is how the members are presented inside the zip file
    # e.g., drone-deploy-0.1.16/templates/...
    default_repo = 'https://github.com/keithdadkins/drone-deploy'
    template_repo = os.getenv('DRONE_DEPLOY_TEMPLATES_REPO', default_repo)
    templates_url = f"{template_repo}/archive/{version.__version__}.zip"
    zip_base_path = f"drone-deploy-{version.__version__}"    
    tempdir = tempfile.mkdtemp()
    r = requests.get(templates_url, allow_redirects=True)
    with tempfile.TemporaryFile() as tmp:
        tmp.write(r.content)
        try:
            with zipfile.ZipFile(tmp) as file:
                if file.testzip() is not None:
                    click.echo(click.style(f"\ttemplate download was corrupted.. exiting",
                                           fg='red'))
                templates = [member for member in file.namelist()
                             if member.startswith(f'{zip_base_path}/templates')]
                file.extractall(path=tempdir, members=templates)
        except Exception as e:
            print(type(e))
            print(e.args)
            print(e)
            click.echo(click.style(f"\terror getting templates... exiting.", fg='red'))
            sys.exit()

        # move files from tmp to templates
        items = Path(tempdir).joinpath(zip_base_path, 'templates').glob('*')
        for item in items:
            shutil.move(str(item), path)

    # cleanup
    shutil.rmtree(tempdir)

    # TODO: verify
    click.echo(f"\tdownloaded templates to {path}")


def setup_templates(path):
    '''copy templates from releases or locally'''
    # if we are running from a release exe, then get the templates from a repo
    # else get them from the local source
    if Path(__file__).name == 'init_cli.py':
        # running from source
        templates_dir = Path(__file__).parent.parent.parent.joinpath('templates')
        if templates_dir.exists():
            shutil.copytree(templates_dir, path)
        # TODO: verify
        click.echo(f"\tcopied templates to {path}")
    else:
        copy_templates_from_repo(path)


def copy_file_from_templates(name, path):
    try:
        src = Path(path).parent.joinpath('templates', f'{name}.template')
        shutil.copy(src, path)
        if Path(path).exists():
            click.echo(f"\tgenerated {name}")
    except FileNotFoundError:
        click.echo(click.style(f"\tcouldn't find {name} in {src.parent}... skipping",
                   fg='yellow'))
    except Exception as e:
        print(type(e))
        print(e.args)
        print(e)


def copy_readme(path):
    copy_file_from_templates('README.md', path)


def copy_gitignore(path):
    copy_file_from_templates('.gitignore', path)


def setup_init_item(item, path):
    items = {
        'deployments': setup_deployments,
        'templates': setup_templates,
        'README.md': copy_readme,
        '.gitignore': copy_gitignore
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
    files = ['.gitignore', 'README.md']
    click.echo(click.style(f"Initializing...", bold=True))
    # stop init if any of the folders exist, else create them
    for folder in folders:
        folder_path = base_path.joinpath(folder).resolve()
        if folder_path.exists():
            click.echo(click.style(f"Stopping init because '{folder_path}' would be destroyed.",
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

    click.echo(f"Successfully initialized {path}")
    if Path(os.getcwd()).resolve() != path.resolve():
        click.echo(
            click.style(f"*** Don't forget to cd into the {Path(path).name} directory before"
                        " creating deployments. ***", bold=True))
