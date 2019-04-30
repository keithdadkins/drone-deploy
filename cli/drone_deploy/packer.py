import os
import sys
import json
import subprocess
from pathlib import Path


class Packer():
    """
    Simple wrapper class for running packer commands.

    Required Attributes
    ----------
    working_dir: directory
        The full path to the deployment directory.

    Methods
    -------


    """
    def __init__(self, working_dir, packer_vars=[]):
        self.working_dir = working_dir
        self.packer_vars = packer_vars
        self.__use_local_cmd()
        self.load_artifacts()

    def __use_local_cmd(self):
        pass
        # # use local packer command
        # def packer(command):
        #     command = f"packer {command} {self.packer_vars}"
        #     p = subprocess.Popen(command, stderr=subprocess.PIPE, shell=True, text=True,
        #                          cwd=self.working_dir, env=os.environ)
        #     while True:
        #         out = p.stderr.read(1)
        #         if out == '' and p.poll() is not None:
        #             break
        #         if out != '':
        #             sys.stdout.write(out)
        #             sys.stdout.flush()
        # self.packer = packer

    def __use_docker_cmd(self):
        '''TODO: Use docker to run packer.'''
        pass

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
            # artifact_id = region:ami (us-east-1:ami-adfsdf23423443)
            build = self.manifest["builds"][0]["artifact_id"].split(':')
            self.drone_server_ami = build[1]

            # drone_deploy_id
            deploy_id = self.manifest["builds"][0]["custom_data"]["drone_deployment_id"]
            self.drone_deployment_id = deploy_id
            self.new_build = False
        except FileNotFoundError:
            self.new_build = True
            self.drone_deployment_id = ''
            self.drone_server_ami = ''
            pass

    def get_deployment_id(self):
        pass

    def get_ami_id(self):
        pass

    def build_ami(self):
        '''Builds the ami for the deployment.'''
        # Just run the build-drone-server-ami.sh script
        # TODO: bring this all into python, or refactor build script to only accept
        # command line args instead of env vars.

        # run the build script in the deployment directory
        build_dir = Path(self.working_dir.parent.resolve())
        command = "./build-drone-server-ami.sh -p"
        # for k, v in os.environ.items():
        #     print(f"{k}={v}")
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
        except Exception as e:
            print(type(e))
            print(e.args)
            print(e)
            return False

        # update the manifest
        self.load_artifacts()
