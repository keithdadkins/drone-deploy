import os
import sys
import subprocess
import boto3
from pathlib import Path


def terraform():
    # tf_path = Path(__file__).parents[2].resolve()
    # tf_path = tf_path.joinpath('terraform')
    tf_path = Path.cwd().joinpath('terraform')
    try:
        if "Terraform" in subprocess.run(["terraform", "version"], capture_output=True, 
                                         text=True).stdout:
            def terraform(command=[]):
                commands = command
                p = subprocess.Popen(commands, stderr=subprocess.PIPE, shell=True, text=True,
                                     cwd=tf_path)
                while True:
                    out = p.stderr.read(1)
                    if out == '' and p.poll() is not None:
                        break
                    if out != '':
                        sys.stdout.write(out)
                        sys.stdout.flush()

            return terraform
    except Exception as e:
        print(type(e))
        print(e.args)
        print(e)

    # terraform isn't install localled, use docker to run
    tf_base_image = os.getenv("TERRAFORM_BASE_IMAGE", default="hashicorp/terraform:latest")

    def terraform(command):
        commands = ["docker", "run", "--rm", "-v", f"{tf_path}:.",
                    f"{tf_base_image}", "--", "terraform"] + command
        retval = subprocess.run(commands, capture_output=True, text=True).stdout
        return retval.strip()
    return terraform


def set_iam_roles_and_policies():
    tf = terraform()
    tf(["terraform apply -target=aws_iam_policy.drone-builder-ec2 \
                         -target=aws_iam_policy.drone-builder-s3 \
                         -target=aws_iam_policy_attachment.ec2 \
                         -target=aws_iam_policy_attachment.s3 \
                         -target=aws_iam_instance_profile.drone-builder"])

    # export the deploy id
    account_id = boto3.client('sts').get_caller_identity().get('Account')
    os.environ['DRONE_BUILDER_ROLE_ARN'] = f"arn:aws:iam::{account_id}:role/drone-builder-role"


def apply():
    tf = terraform()
    tf(["terraform apply"])
