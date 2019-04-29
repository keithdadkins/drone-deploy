import os
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
    """

    def __load_param(self, param_name):
        '''load config from env or from config.yaml if env is not set'''
        param = os.getenv(param_name.upper()) or self.config.get(param_name, None)
        if param_name == "aws_region":
            self.config.get(param_name, self.config['drone_aws_region'])
        self.config[param_name] = param

        # handle yaml arrays to hcl array
        if type(param) == ruamel.yaml.comments.CommentedSeq:
            # array
            patched_param = str(param).replace("'", '"')
            self.tf_vars.append((param_name, patched_param))
        else:
            self.tf_vars.append((param_name, f"\"{param}\""))
            print(param)
        return param

    def __init__(self, config_file):
        '''Load and parse the deployment config.'''
        # use ruamel to parse config file (preserves comments)
        yaml = YAML()
        self.config_file = config_file
        self.config = yaml.load(self.config_file)

        # list of tuples we want to pass along to terraform (added in __load_params)
        self.tf_vars = []

        # load deployment settings from env or config.yaml if env is not set
        self.__load_param("drone_aws_region")
        self.__load_param("drone_vpc_id")
        self.__load_param("drone_server_host_name")
        self.__load_param("drone_server_hosted_zone")
        self.__load_param("drone_server_key_pair_name")
        self.__load_param("drone_server_instance_type")
        self.__load_param("drone_docker_compose_version")
        self.__load_param("drone_server_allow_http")
        self.__load_param("drone_server_allow_https")
        self.__load_param("drone_server_allow_ssh")
        self.__load_param("drone_open")
        self.__load_param("drone_admin")
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
        self.__load_param("drone_server_ami")
        self.__load_param("drone_deployment_id")
        self.__load_param("drone_builder_role_arn")
        self.__load_param("aws_region")

        # prepare terraform for running commands
        self.setup_terraform()
        self.setup_packer()

    def __str__(self):
        '''returns pretty formatted yaml'''
        return str(ruamel.yaml.round_trip_dump(self.config))

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
        self.packer = Packer(packer_dir)

    def init(self):
        # run terraform init in the deployment dir
        self.terraform.init()

    def bootstrap_roles_and_policies(self):
        # setup needed iam roles and permissions for building/launching ami
        self.terraform.bootstrap_roles_and_policies()

    def plan(self):
        self.terraform.plan()

    def build_ami(self):
        self.packer.build_ami()

    def deploy(self):
        '''apply terraform resources'''
        # TODO: get from env
        os.environ['DRONE_BUILDER_ROLE_ARN'] = "arn:aws:iam::566612972112:role/drone-builder-role"
        print(self.terraform.tf_vars)
        self.terraform.apply()
