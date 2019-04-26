import sys
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
        self.config = yaml.load(self.config_file)

    def __str__(self):
        '''returns pretty formatted yaml'''
        return str(ruamel.yaml.round_trip_dump(self.config))

    def write_config(self):
        yaml = YAML()
        with open(self.config_file, 'w') as file:
            yaml.dump(self.config, file)
