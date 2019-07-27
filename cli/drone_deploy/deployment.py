import os
import secrets
import ruamel.yaml
from pathlib import Path
from ruamel.yaml import YAML
from drone_deploy.packer import Packer
from drone_deploy.terraform import Terraform


class Deployment():
    """
    Base class that represents a drone deployment configuration. Specifically, it loads and
    parses a /deployments/$name/config.yaml.

    Usage:
        config_file = Path('/path/to/config/file')
        deployment = Deployment(config_file)

        Get deployment settings:
        print(deployment.config['aws_region'])      => 'us-east-1'

        Set values:
        deployment.config['aws_region'] = 'us-east-2'
        print(deployment.config['aws_region'])      => 'us-east-2'

        Arrays:
        deployment.config['drone_server_allow_ssh'][0] = '12.12.12.0/32'
        deployment.config['drone_server_allow_ssh'][1] = '67.89.12.23/32'

    ...

    Required Attributes
    ----------
    config_file: file
        The full path to our drone config.yaml file.

    Methods
    -------
    __init__(self, config_file)
        Loads the config.yaml file.
    write_config(self)
        Writes self.config to disk.
    TODO: finish documenting class
    """

    def __load_param(self, param_name):
        '''load config from env or from config.yaml if env is not set'''
        if os.getenv(param_name.upper()):
            # env var exists, set param to its value
            param = os.getenv(param_name.upper(), '')
        else:
            # get the value from the config file and export as an env var
            param = self.config.get(param_name, '')
            os.environ[param_name.upper()] = str(param)

        # generate a random rpc_secret if not set
        if param_name == "drone_rpc_secret":
            if not param and os.environ.get('DRONE_RPC_SECRET') in ("None", ""):
                param = self.generate_rpc()

        # dynamically name the s3 bucket
        if param_name == "drone_s3_bucket":
            if not param and os.environ.get('DRONE_S3_BUCKET') in ("None", ""):
                machine_name = os.environ.get('DRONE_SERVER_MACHINE_NAME')
                hosted_zone = os.environ.get('DRONE_SERVER_HOSTED_ZONE')
                if machine_name and hosted_zone:
                    param = f"drone-data.{machine_name}.{hosted_zone}"

        # set config entry
        self.config[param_name] = param

        # get the 'drone_builder_role_arn' from terraform
        if param_name == "drone_builder_role_arn":
            self.config[param_name] = self.terraform.drone_builder_role_arn

        # get the 'drone_deployment_id' from packer
        if param_name == "drone_deployment_id" and not param:
            self.config[param_name] = self.packer.drone_deployment_id
            os.environ[param_name.upper()] = self.config[param_name]
            param = self.config[param_name]

        # get the drone_server_ami from packer
        if param_name == "drone_server_ami" and not param:
            self.config[param_name] = self.packer.drone_server_ami
            os.environ[param_name.upper()] = self.config[param_name]
            param = self.config[param_name]

        # flatten user-filter for docker-compose (convert from ruamel and remove brackets), ticks, and spaces
        if param_name == "drone_user_filter":
            patched_param = []
            patched_param = list(param)
            param = repr(patched_param).replace('[', '').replace(']', '').replace("'", "").replace(" ", "")

        # convert yaml arrays to something hashi compatable.
        if type(param) == ruamel.yaml.comments.CommentedSeq:
            patched_param = str(param).replace("'", '"')
            self.tf_vars.append((param_name, patched_param))
            param = patched_param
        else:
            self.tf_vars.append((param_name, f"\"{param}\""))

        # export configs so they are available in terraform, as terraform automatically
        # picks up env vars whose names start with TF_VAR_
        os.environ[f"TF_VAR_{param_name.lower()}"] = str(param)
        return param

    def __init__(self, config_file):
        '''
        Load and parse the deployment config.yaml file.
        I'm using 'ruamel' to parse config file as it preserves yaml comments.
        '''
        yaml = YAML()
        self.config_file = config_file
        self.config = yaml.load(self.config_file)

        # list of tuples we'll want to pass to terraform/packer (added via self.__load_param())
        self.tf_vars = []

        # The 'drone_deployment_name' is dynamically created from the name of the deployment
        # directory and is used for naming resources in AWS. In order to keep aws resources
        # clearly labeled we append 'drone' to the name if the user hasn't already. E.g.,
        # 'drone-deploy new dev' creates dir '/deployments/dev' and creates 'drone-dev-foo' aws resource name
        if not os.getenv('DRONE_DEPLOYMENT_NAME'):
            if not self.config.get('drone_deployment_name'):
                # deployment name wasn't overidden via env var or in the config.yaml file, so
                # set the env var here and let __load_param handle everything else
                if 'drone' in self.config_file.parent.name:
                    os.environ['DRONE_DEPLOYMENT_NAME'] = f"{self.config_file.parent.name}"
                else:
                    os.environ['DRONE_DEPLOYMENT_NAME'] = f"drone-{self.config_file.parent.name}"
        self.__load_param("drone_deployment_name")
        self.__load_param("drone_aws_region")
        self.__load_param("drone_vpc_id")
        self.__load_param("drone_server_machine_name")
        self.__load_param("drone_server_hosted_zone")
        self.__load_param("drone_server_key_pair_name")
        self.__load_param("drone_server_instance_type")
        self.__load_param("drone_docker_compose_version")
        self.__load_param("drone_server_allow_http")
        self.__load_param("drone_server_allow_https")
        self.__load_param("drone_server_allow_ssh")
        self.__load_param("drone_open")
        self.__load_param("drone_admin")
        self.__load_param("drone_admin_email")
        self.__load_param("drone_user_filter")
        self.__load_param("drone_github_server")
        self.__load_param("drone_github_client_id")
        self.__load_param("drone_github_client_secret")
        self.__load_param("drone_agents_enabled")
        self.__load_param("drone_tls_autocert")
        self.__load_param("drone_server_proto")
        self.__load_param("drone_server_host")
        self.__load_param("drone_cli_version")
        self.__load_param("drone_server_docker_image")
        self.__load_param("drone_agent_docker_image")
        self.__load_param("drone_server_base_ami")
        self.__load_param("aws_cli_base_image")
        self.__load_param("drone_rpc_secret")
        self.__load_param("drone_s3_bucket")

        # prepare terraform
        self.setup_terraform()
        self.__load_param("drone_builder_role_arn")

        # prepare packer
        self.setup_packer()
        self.__load_param("drone_deployment_id")
        self.__load_param("drone_server_ami")

        # is this a new deployment?
        if self.packer.new_build and self.terraform.has_tf_state:
            self.new_deployment = True
        else:
            self.new_deployment = False

    def __str__(self):
        '''returns pretty formatted yaml'''
        return str(ruamel.yaml.round_trip_dump(self.config))

    def generate_rpc(self, num_bytes=16):
        '''returns a random hexadecimal token (defaults to 128bit) '''
        return secrets.token_hex(num_bytes)

    def write_config(self):
        '''writes the self.config object to disk'''
        yaml = YAML()
        with open(self.config_file, 'w') as file:
            yaml.dump(self.config, file)

    def setup_terraform(self):
        '''Setup our Terraform command wrapper.'''
        tf_dir = Path(self.config_file).parent.joinpath('terraform').resolve()
        self.terraform = Terraform(tf_dir, tf_vars=self.tf_vars)

    def setup_packer(self):
        '''Setup our Packer command wrapper.'''
        packer_dir = Path(self.config_file).parent.joinpath('packer').resolve()
        packer_vars = [(k, v) for k, v in self.config.items()]
        self.packer = Packer(packer_dir, packer_vars=packer_vars)

    def init(self):
        '''runs terraform init in the deployment dir'''
        self.terraform.init()

    def plan(self):
        '''runs terraform plan in the deployment dir'''
        self.terraform.plan()

    def build_ami(self):
        '''builds the drone server ami using packer'''
        self.packer.build_ami()

    def deploy(self, targets=[]):
        '''runs `terraform apply`'''
        self.terraform.apply(targets)

    def destroy(self):
        '''destroys/deletes terraform resources and directory (optional)'''
        self.terraform.destroy()

    def deployment_status(self, deployment_name):
        '''returns the current state of the deployment'''
        # packer
        if self.packer.new_build:
            print(f"AMI has not been built. Run 'drone-deploy prepare {deployment_name}'"
                  f"and 'drone-deploy build-ami {deployment_name}' to build")
