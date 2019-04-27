import ruamel.yaml
from ruamel.yaml import YAML


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

    def __init__(self, config_file):
        '''Load and parse the config.yaml.'''
        # use ruamel to parse config file (preserves comments)
        yaml = YAML()
        self.config_file = config_file
        config = yaml.load(self.config_file)

        # load settings
        # TODO: validate settings
        # TODO: getters and setters so we can edit settings from cli
        self.aws_region = config.get("aws_region")
        self.vpc_id = config.get("vpc_id")
        self.drone_deployment_id = config.get("drone_deployment_id")
        self.drone_server_machine_name = config.get("drone_server_machine_name")
        self.drone_server_hosted_zone = config.get("drone_server_hosted_zone")
        self.drone_server_ami = config.get("drone_server_ami")
        self.drone_server_key_pair_name = config.get("drone_server_key_pair_name")
        self.drone_server_instance_type = config.get("drone_server_instance_type")
        self.drone_server_allow_http = config.get("drone_server_allow_http")
        self.drone_server_allow_https = config.get("drone_server_allow_https")
        self.drone_server_allow_ssh = config.get("drone_server_allow_ssh")
        self.config = config

    def __str__(self):
        '''returns pretty formatted yaml'''
        return str(ruamel.yaml.round_trip_dump(self.config))

    def write_config(self):
        '''writes the self.config object to disk'''
        yaml = YAML()
        with open(self.config_file, 'w') as file:
            yaml.dump(self.config, file)

    def plan():
        pass

    def apply():
        pass