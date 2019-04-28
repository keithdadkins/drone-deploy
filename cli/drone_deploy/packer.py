import sys
import subprocess


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
    def __init__(self, working_dir):
        self.working_dir = working_dir
        self.__use_local_cmd()

    def __use_local_cmd(self):
        # use local packer command
        def packer(command):
            command = f"packer {command}"
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
        '''TODO: Use docker to run terraform.'''
        pass

    def build_ami(self):
        '''Builds the ami for the deployment.'''
        pass