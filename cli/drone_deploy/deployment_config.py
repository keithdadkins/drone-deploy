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

    @staticmethod
    def parse_yaml(yml):
        '''parse yaml file or stream'''
        if type(yml) is pathlib.PosixPath:
            file = open(yml, 'r')
            return yaml.safe_load(file)
        else:
            return yaml.safe_load(yml)
