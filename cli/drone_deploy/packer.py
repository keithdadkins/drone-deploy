import os
import sys
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

    def __use_local_cmd(self):
        # use local packer command
        def packer(command):
            command = f"packer {command} {self.packer_vars}"
            p = subprocess.Popen(command, stderr=subprocess.PIPE, shell=True, text=True,
                                 cwd=self.working_dir)
            while True:
                out = p.stderr.read(1)
                if out == '' and p.poll() is not None:
                    break
                if out != '':
                    sys.stdout.write(out)
                    sys.stdout.flush()
        self.packer = packer

    def __use_docker_cmd(self):
        '''TODO: Use docker to run packer.'''
        pass

    @property
    def packer_vars(self):
        """Returns formatted vars ready for packer cmd ex. -var foo=bar -var biz=baz"""
        output = ' '.join(["-var {0}={1}".format(k, v) for k, v in self.__packer_vars.items()])
        return output

    @packer_vars.setter
    def packer_vars(self, packer_vars):
        # unpacks packers vars (a list of tuples) into a dict
        self.__packer_vars = {k: v for k, v in packer_vars}

    def build_ami(self):
        '''Builds the ami for the deployment.'''
        # Just run the build-drone-server-ami.sh script
        # TODO: bring this all into python, or refactor build script to only accept
        # command line args instead of env vars.

        # cd into the deployment folder and run the build script
        build_dir = Path(self.working_dir.parent.resolve())
        command = "./build-drone-server-ami.sh -p"

        p = subprocess.Popen(command, stderr=subprocess.PIPE, shell=True, text=True,
                             cwd=build_dir)
        while True:
            out = p.stderr.read(1)
            if out == '' and p.poll() is not None:
                break
            if out != '':
                sys.stdout.write(out)
                sys.stdout.flush()
