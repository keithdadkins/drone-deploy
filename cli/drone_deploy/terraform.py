import os
import sys
import json
import subprocess
from pathlib import Path


class Terraform():
    """
    Simple wrapper class for running terraform commands. The main Deployment class creates an
    instance of this class when a deployment is instantiated. E.g.,
        deployment = Deployment(config_file)
        deployment.terraform.plan()

    Required Attributes
    ----------
    working_dir: directory
        The full path to the directory with .tf resources.

    Properties
    ----------
    tf_vars: list
        A list of terraform variables (tuples) to run with each terraform command.
    drone_builder_role_arn: string
        Automatically set if an ARN is found in the deployments tfstate file.

    Methods
    -------
    __use_local_cmd
        Defines a class method to proxy terraform. The '__use_local_cmd' is there as initially
        the idea was to allow the user to run terraform from docker or locally if installed.
        Only locally is supported for now as mounting .gitconfig, deployment dirs, etc is not
        ideal.
    load_tf_state
        Loads terraform state file if present.
    init
        Runs `terraform init` in the deployment dir.
    plan
        Runs `terraform plan` in the deployment dir.
    apply
        Runs `terraform apply` in the deployment dir.
    destroy
        Runs `terraform destroy` in the deployment dir.
    """
    SUPPORTED_TF_VERSION = 'Terraform v0.11.14'
    TERRAFORM_VERSION_MSG = f"""
    {SUPPORTED_TF_VERSION} is the only version of Terraform currently supported because
    terraform underwent a major upgrade (v11 -> v12) during development which introduced
    breaking changes in the TF configuration language.

    Please install {SUPPORTED_TF_VERSION} and try again.

    """

    def __init__(self, working_dir, tf_vars=[]):
        # tfvars should be a list of tuples (key,value)
        self.working_dir = working_dir
        self.tf_vars = tf_vars
        self.__use_local_cmd()

        # try to load tf state file if present
        self.load_tf_state()

    def __use_local_cmd(self):
        '''
        Define a class method to proxy terraform.
        '''
        def terraform(command, tf_targets=None, tf_args=None):
            # set flags and base command
            tfverbose = False
            tfout = False
            tfplan = False
            tfplanfile = Path(self.working_dir).joinpath('tfplan')
            tfpostmsg = ""
            if command == 'plan':
                tfout = True
                tfpostmsg = "To apply these exact changes, run `drone-deploy deploy`."
            if command in ['apply']:
                if tfplanfile.exists():
                    tfplan = True
            command = f"TF_IN_AUTOMATION={tfverbose} terraform {command}"

            # append -out=file if set
            if tfout:
                command = f"{command} -out=tfplan"

            # append targets if present
            if tf_targets:
                command = f"{command} {tf_targets}"

            # append args if present
            if tf_args:
                command = f"{command} {tf_args}"

            # use plan file if present
            if tfplan:
                command = f"{command} tfplan"

            # pass our env vars along to the sub process when executed
            env = os.environ
            p = subprocess.Popen(command, stderr=subprocess.PIPE, shell=True, text=True,
                                 cwd=self.working_dir, env=env)
            while True:
                out = p.stderr.read(1)
                if out == '' and p.poll() is not None:
                    break
                if out != '':
                    sys.stdout.write(out)
                    sys.stdout.flush()
            if tfpostmsg:
                print(f"\n{tfpostmsg}\n")

            # check for errors
            if p.returncode != 0:
                # check for valid terraform version
                print("Something went wrong running terraform commands... ")
                current_ver = subprocess.call(["terraform", "version"])
                if current_ver != self.SUPPORTED_TF_VERSION:
                    print(self.TERRAFORM_VERSION_MSG)

        self.terraform = terraform

    @property
    def tf_vars(self):
        """Returns formatted vars ready for terraform cmd ex. -var='foo=bar' -var='biz=baz'"""
        output = ' '.join(["-var '{0}={1}'".format(k, v) for k, v in self.__tf_vars.items()])
        return output

    @tf_vars.setter
    def tf_vars(self, tf_vars):
        # unpacks tf vars
        self.__tf_vars = {k: v for k, v in tf_vars}

    @property
    def drone_builder_role_arn(self):
        '''Checks tfstate for arn if it exists'''
        try:
            dbra = self.tf_state["modules"][0]["outputs"]
            arn = dbra["DRONE_BUILDER_ROLE_ARN"]["value"]
            os.environ['DRONE_BUILDER_ROLE_ARN'] = arn
            return arn
        except Exception:
            return ''

    @drone_builder_role_arn.setter
    def drone_builder_role_arn(self, arn):
        '''Sets drone_builder_role_arn.'''
        self.drone_builder_role_arn = arn

    def load_tf_state(self):
        '''Loads terraform state file if present.'''
        try:
            state_file = self.working_dir.joinpath('terraform.tfstate').resolve()
            with open(state_file, "r") as read_file:
                self.tf_state = json.load(read_file)
            self.has_tf_state = True
        except Exception:
            self.has_tf_state = False

    def init(self):
        '''Runs 'terraform init' in the working directory.'''
        self.terraform("init")

    def plan(self, tf_targets=[]):
        '''Runs 'terraform plan' in the working directory.'''
        self.terraform("plan", tf_targets)

    def apply(self, tf_targets=[]):
        '''Runs 'terraform apply' in the working directory.'''
        self.terraform("apply", tf_targets)

    def destroy(self, tf_targets=[]):
        '''Runs 'terraform destroy' in the working directory.'''
        self.terraform("destroy", tf_targets)
