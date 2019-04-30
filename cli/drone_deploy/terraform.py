import os
import sys
import json
import subprocess


class Terraform():
    """
    Simple wrapper class for running terraform commands.

    Can run terraform commands via Docker or locally if installed.

    Required Attributes
    ----------
    working_dir: directory
        The full path to the directory with .tf resources.

    Optional Attributes
    ----------
    tf_vars: list
        A list of terraform varibles (in key, value pairs format) to
        run with each terraform command (apply, plan, etc).

    Methods
    -------


    """
    def __init__(self, working_dir, tf_vars=[]):
        # tfvars should be a list of tuples (key,value)
        self.working_dir = working_dir
        self.tf_vars = tf_vars
        self.__use_local_cmd()
        self.load_outputs()

    def __use_local_cmd(self):
        # terraform is installed
        def terraform(command, tf_targets=None, tf_args=None):
            if tf_targets:
                command = f"terraform {command} {self.tf_vars} {tf_targets}"
            else:
                command = f"terraform {command} {self.tf_vars}"

            if tf_args:
                command = f"{command} {tf_args}"

            # pass our env vars along to the sub process
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
        self.terraform = terraform

    def __use_docker_cmd():
        '''TODO: Use docker to run terraform.'''
        pass

    @property
    def tf_vars(self):
        """Returns formatted vars ready for terraform cmd ex. -var='foo=bar' -var='biz=baz'"""
        output = ' '.join(["-var '{0}={1}'".format(k, v) for k, v in self.__tf_vars.items()])
        return output

    @tf_vars.setter
    def tf_vars(self, tf_vars):
        # unpacks tf vars (a list of tuples) into a dict
        self.__tf_vars = {k: v for k, v in tf_vars}

    def init(self):
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

    def bootstrap_roles_and_policies(self):
        '''Applies needed IAM roles and policies for building/deploying ami.'''
        targets = ' '.join("-target={}".format(t) for t in [
            "aws_iam_policy.drone-builder-ec2",
            "aws_iam_policy.drone-builder-s3",
            "aws_iam_policy_attachment.ec2",
            "aws_iam_policy_attachment.s3",
            "aws_iam_instance_profile.drone-builder"
        ])
        self.terraform("apply", targets)

    def status(self):
        pass

    def load_outputs(self):
        '''loads terraform outputs from tfstat in json format'''
        # try to load terraform.tfstate file
        try:
            state_file = self.working_dir.joinpath('terraform.tfstate').resolve()
            with open(state_file, "r") as read_file:
                self.tf_state = json.load(read_file)
            dbra = self.tf_state["modules"][0]["outputs"]
            self.drone_builder_role_arn = dbra["DRONE_BUILDER_ROLE_ARN"]["value"]
            os.environ['DRONE_BUILDER_ROLE_ARN'] = self.drone_builder_role_arn
        except Exception:
            self.drone_builder_role_arn = ""
            self.tf_state = {}
