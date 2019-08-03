import os
import sys
import json
import subprocess
from pathlib import Path


class Packer():
    """
    Simple wrapper class for running packer commands. The main Deployment class creates an
    instance of this class when a deployment is instantiated. E.g.,
        deployment = Deployment(config_file)
        deployment.packer.build_ami()

    Required Attributes
    ----------
    working_dir: directory
        The full path to the deployment directory.

    Properties
    ----------
    packer_vars
        Returns vars formatted for when calling packer via the cli. E.g. '-var foo=bar -var biz=baz'.

    Methods
    -------
    __init__(self, working_dir, packer_vars=[])
        Sets up deployment specific settings
        working_dir and packer_vars are provided when a Deployment is instantiated.
    load_artifacts
        Attempts to get info from any previous builds (from packers manifest file).
    build_ami
        Builds the AMI for a deployment. 
        All this currently does is run the `build-drone-server-ami.sh` bash script and
        runs the load_artifacts method when complete to update build info.
    """

    def __init__(self, working_dir, packer_vars=[]):
        self.working_dir = working_dir
        self.packer_vars = packer_vars
        self.load_artifacts()

    @property
    def packer_vars(self):
        """Returns formatted vars ready for packer cmd ex. -var foo=bar -var biz=baz"""
        output = ' '.join(["-var {0}={1}".format(k, v) for k, v in self.__packer_vars.items()])
        return output

    @packer_vars.setter
    def packer_vars(self, packer_vars=[]):
        # unpacks packers vars (a list of tuples) into a dict
        self.__packer_vars = {k: v for k, v in packer_vars}

    def load_artifacts(self):
        '''loads build artifacts as attributes from manfiest.json file'''
        # try to load manifest file
        try:
            manifest_file = self.working_dir.joinpath('manifest.json').resolve()
            with open(manifest_file, "r") as read_file:
                self.manifest = json.load(read_file)
            self.new_build = False
            
            # artifact_id = region:ami (us-east-1:ami-adfsdf23423443)
            build = self.manifest["builds"][0]["artifact_id"].split(':')
            self.drone_server_ami = build[1]

            # drone_deploy_id
            deploy_id = self.manifest["builds"][0]["custom_data"]["drone_deployment_id"]
            self.drone_deployment_id = deploy_id

        except FileNotFoundError:
            self.new_build = True
            self.drone_deployment_id = ''
            self.drone_server_ami = ''
            pass

        except json.decoder.JSONDecodeError as e:
            print("The packer manifest.json file appears to be corrupt.")
            print(f"Please review {manifest_file} for errors and either fix or remove.")
            print("---------")
            print(type(e))
            print(e.args)
            print(e)
            return e

    def build_ami(self):
        '''Builds the ami for the deployment.'''
        # Just run the build-drone-server-ami.sh script
        # TODO: bring this all into python, or refactor build script to only accept
        # command line args instead of env vars.

        # run the build script in the deployment directory
        build_dir = Path(self.working_dir.parent.resolve())
        command = "./build-drone-server-ami.sh -p"
        try:
            p = subprocess.Popen(command, stderr=subprocess.PIPE, shell=True, text=True,
                                 cwd=build_dir, env=os.environ)
            while True:
                out = p.stderr.read(1)
                if out == '' and p.poll() is not None:
                    break
                if out != '':
                    sys.stdout.write(out)
                    sys.stdout.flush()

            # update the manifest
            self.load_artifacts()

        except Exception as e:
            self.load_artifacts()
            print(type(e))
            print(e.args)
            print(e)
            return False
