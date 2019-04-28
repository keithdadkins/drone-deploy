import sys
import subprocess
from pathlib import Path


class Terraform():
    """
    Simple wrapper class for running terraform commands.

    Can run terraform commands via Docker or locally if installed.

    Required Attributes
    ----------
    working_dir: directory
        The full path to the directory with .tf resources.

    Methods
    -------


    """
    def __init__(self, working_dir, tf_vars=[]):
        # tfvars should be a list of tuples (key,value)
        self.working_dir = working_dir
        self.tf_vars = tf_vars
        self.__use_local_cmd()

    def __use_local_cmd(self):
        # '''Sets self.terraform function to use local terraform.'''
        # try:
        #     if "Terraform" not in subprocess.run(
        #             ["terraform", "version"], capture_output=True, text=True
        #     ).stdout:
        #         print("Couldn't locate 'terraform'. Try installing with your favorite packer"
        #               "manager, or download it from https://www.terraform.io/downloads.html")
        #         sys.exit()
        # except Exception as e:
        #     print(type(e))
        #     print(e.args)
        #     print(e)

        # terraform is installed
        def terraform(command):
            command = f"terraform {command} {self.tf_vars}"
            p = subprocess.Popen(command, stderr=subprocess.PIPE, shell=True, text=True,
                                 cwd=self.working_dir)
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

    def init(self):
        self.terraform("init")

    @property
    def tf_vars(self):
        """returns formatted vars ready for terraform cmd ex. -var='foo=bar' -var='biz=baz'"""
        output = ' '.join(["-var '{0}={1}'".format(k, v) for k, v in self.__tf_vars.items()])
        return output

    @tf_vars.setter
    def tf_vars(self, tf_vars):
        # unpacks tf vars (a list of tuples) into a dict
        self.__tf_vars = {k: v for k, v in tf_vars}

    def plan(self):
        self.terraform("plan")

    def apply():
        pass


# wkdir = Path.cwd().parent.joinpath('deployments/foo/terraform').resolve()
# wkdir = "/Users/foo/projects/podchaser-drone-ami-builder/deployments/foo/terraform"
# terra = Terraform(wkdir)
# terra.init()
# print(terra.plan())

# def terraform():
#     # tf_path = Path(__file__).parents[2].resolve()
#     # tf_path = tf_path.joinpath('terraform')
#     tf_path = Path.cwd().joinpath('terraform')
#     try:
#         if "Terraform" in subprocess.run(["terraform", "version"], capture_output=True, 
#                                          text=True).stdout:
#             def terraform(command=[]):
#                 commands = command
#                 p = subprocess.Popen(commands, stderr=subprocess.PIPE, shell=True, text=True,
#                                      cwd=tf_path)
#                 while True:
#                     out = p.stderr.read(1)
#                     if out == '' and p.poll() is not None:
#                         break
#                     if out != '':
#                         sys.stdout.write(out)
#                         sys.stdout.flush()

#             return terraform
#     except Exception as e:
#         print(type(e))
#         print(e.args)
#         print(e)

#     # terraform isn't install localled, use docker to run
#     tf_base_image = os.getenv("TERRAFORM_BASE_IMAGE", default="hashicorp/terraform:latest")

#     def terraform(command):
#         commands = ["docker", "run", "--rm", "-v", f"{tf_path}:.",
#                     f"{tf_base_image}", "--", "terraform"] + command
#         retval = subprocess.run(commands, capture_output=True, text=True).stdout
#         return retval.strip()
#     return terraform


# def set_iam_roles_and_policies():
#     tf = terraform()
#     tf(["terraform apply -target=aws_iam_policy.drone-builder-ec2 \
#                          -target=aws_iam_policy.drone-builder-s3 \
#                          -target=aws_iam_policy_attachment.ec2 \
#                          -target=aws_iam_policy_attachment.s3 \
#                          -target=aws_iam_instance_profile.drone-builder"])

#     # export the deploy id
#     account_id = boto3.client('sts').get_caller_identity().get('Account')
#     os.environ['DRONE_BUILDER_ROLE_ARN'] = f"arn:aws:iam::{account_id}:role/drone-builder-role"


# def apply():
#     tf = terraform()
#     tf(["terraform apply"])
