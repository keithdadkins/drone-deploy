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
        if os.getenv(param_name.upper()):
            # env var exists TODO: test if counts null/unset vars as valid
            param = os.getenv(param_name.upper())
        else:
            # set the param and export as env var
            param = self.config.get(param_name, '')
            os.environ[param_name.upper()] = str(param)

        if param_name == "drone_builder_role_arn":
            self.config[param_name] = self.terraform.drone_builder_role_arn
        else:
            self.config[param_name] = param

        if param_name == "drone_deployment_id" and not param:
            self.config[param_name] = self.packer.drone_deployment_id
            os.environ[param_name.upper()] = self.config[param_name]
            param = self.config[param_name]

        if param_name == "drone_server_ami" and not param:
            self.config[param_name] = self.packer.drone_server_ami
            os.environ[param_name.upper()] = self.config[param_name]
            param = self.config[param_name]

        # handle yaml arrays to hcl array
        if type(param) == ruamel.yaml.comments.CommentedSeq:
            # array
            patched_param = str(param).replace("'", '"')
            self.tf_vars.append((param_name, patched_param))
            param = patched_param
        else:
            self.tf_vars.append((param_name, f"\"{param}\""))

        # export params to for terraform
        os.environ[f"TF_VAR_{param_name.lower()}"] = str(param)
        return param

    def __init__(self, config_file):
        '''Load and parse the deployment config.'''
        # use ruamel to parse config file (preserves comments)
        yaml = YAML()
        self.config_file = config_file
        self.config = yaml.load(self.config_file)

        # list of tuples we want to pass along to terraform/packer (added in __load_params)
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
        self.__load_param("drone_agent_docker_image")
        self.__load_param("aws_cli_base_image")
        self.__load_param("drone_server_base_ami")
        # self.__load_param("aws_region")

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
        # run terraform init in the deployment dir
        self.terraform.init()

    def plan(self):
        self.terraform.plan()

    def build_ami(self):
        # build the ami
        self.packer.build_ami()

        # # set build artifacts (overides existing env vars)
        # try:
        #     self.drone_deployment_id = self.packer.drone_deployment_id
        #     self.drone_server_ami = self.packer.ami_id
        #     os.environ['DRONE_DEPLOYMENT_ID'] = self.drone_deployment_id
        #     os.environ['DRONE_SERVER_AMI'] = self.drone_server_ami
        # except AttributeError:
        #     print("Could not load deployment. Check your settings and try rebuilding the ami.")

    def deploy(self, targets=[]):
        '''apply terraform resources'''
        self.terraform.apply(targets)

    def destroy(self):
        '''destroys terraform resources'''
        self.terraform.destroy()

    def deployment_status(self, deployment_name):
        '''returns the state of the deployment'''   

        # if self.terraform.has_tf_state:
        #     items = self.terraform.tf_state['modules'][0]['resources']
        # else:
        #     items = {}

        # print("The following resources have been deployed:")
        # for k, v in items.items():
        #     print(f"    {k}")

        # packer
        if self.packer.new_build:
            print(f"AMI has not been built. Run 'drone-deploy prepare {deployment_name}'"
                  f"and 'drone-deploy build-ami {deployment_name}' to build")
