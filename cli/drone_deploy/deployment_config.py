import yaml
import pathlib


class DeploymentConfigImportError(Exception):
    pass


class DeploymentConfigImportNameError(Exception):
    pass


class DeploymentConfigInvalidDataError(Exception):
    pass


class DeploymentConfig():
    """
    Base class that represents a drone deployment configuration. Specifically, it loads and
    parses a /deployments/$name/config.yaml. It can import and export env vars, yaml, and hcl.

    Usage:
        config_file = Path('/path/to/config/file')
        config = DeploymentConfig(config_file)
        
        Get values:
        print(config['aws_region']) => 'us-east-1'

        Set values:
        config['aws_region'] = 'us-east-2'
        print(config['aws_region']) => 'us-east-2'

        Arrays:
        config['drone_server_allow_ssh'][0] = '12.12.12.0/32'
        config['drone_server_allow_ssh'][1] = '67.89.12.23/32'

    ...

    Required Attributes
    ----------
    config_file: file
        The full path to the config file.

    Methods
    -------
    __init__(self, config_file)
        Loads the config.yaml file.
    parse_yaml(self, yaml)
        Parses yaml into self.configuration
    """

    def __init__(self, config_file):
        '''Loads the config file. Errors if unsuccessful'''
        self.config_file = config_file
        self.configuration = self.parse_yaml(config_file)

    def __str__(self):
        '''returns configuration as formatted yaml'''
        return yaml.dump(self.configuration)

    def save(self):
        '''saves the current configuration to file, overwriting existing file.'''
        with open(self.config_file, 'w') as config_file:
            yaml.dump(self.configuration, config_file, default_flow_style=False)

    def load(self):
        '''loads or reloads the config.yaml file'''
        self.__init__(self.config_file)

    @staticmethod
    def parse_yaml(yml):
        '''parse yaml file or stream'''
        if type(yml) is pathlib.PosixPath:
            file = open(yml, 'r')
            return yaml.safe_load(file)
        else:
            return yaml.safe_load(yml)


# config_file = pathlib.Path('../deployments/foobar/config.yaml').resolve()
# deployment = DeploymentConfig(config_file)
# print(config['aws_region'])
# config['aws_region'] = 'us-east-2'
# print(config['aws_region'])
# print(type(config.configuration))
# config.save()
# config = DeploymentConfig.load()
# print(config['aws_region'])