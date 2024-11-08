from ..tools.enums import Enum
from typing import Optional, Union, Any, Type
from pathlib import Path
from tempfile import gettempdir
from master.tools.collection import LastIndexOrderedSet, OrderedSet
import platform
import argparse
import sys
import json
import logging


class Mode(Enum):
    """Enum for defining ERP modes."""
    STAGING = 'staging'
    PRODUCTION = 'production'


class LoggerType(Enum):
    CRITICAL = 'CRITICAL'
    FATAL = 'FATAL'
    ERROR = 'ERROR'
    WARNING = 'WARNING'
    WARN = 'WARN'
    INFO = 'INFO'
    DEBUG = 'DEBUG'
    NOTSET = 'NOTSET'


class ArgumentParser:
    """Handles parsing and storage of system settings and configuration for ERP."""
    __slots__ = ('setting', 'configuration')

    def __init__(self, mode: Union[str, Mode], configuration: dict):
        """
        Initializes ArgumentParser with ERP mode and configuration settings.
        Args:
            mode (Union[str, ErpMode]): Operational mode of ERP ('staging' or 'production').
            configuration (dict): ERP configuration settings.
        Raises:
            AssertionError: If mode is not provided.
        """
        assert mode, 'Mode cannot be empty'
        if not isinstance(mode, Mode):
            mode = Mode.from_value(mode.lower())

        # Basic system settings
        self.setting = {
            'system': platform.system(),
            'python': platform.python_version(),
            'mode': mode,
        }

        # Default configuration settings
        self.configuration = configuration
        self.setdefault('log_file', str(Path(gettempdir()).joinpath('MASTER.log')), str)
        self.setdefault('log_level', LoggerType.DEBUG.value, str)
        self.setdefault('db_hostname', 'localhost', str)
        self.setdefault('db_port', 5432, int)
        self.setdefault('db_password', 'postgres', str)
        self.setdefault('db_user', 'postgres', str)
        self.setdefault('db_name', 'master', str)
        self.setdefault('hostname', 'localhost', str)
        self.setdefault('port', 9000, int)
        self.setdefault('websocket_port', 9001, int)
        self.setdefault('pipeline_port', 9002, int)
        self.setdefault('git', [], list)
        self.setdefault('addons', [], list)

        # Ensure unique sets for 'addons' and 'git' settings
        self.configuration['addons'] = LastIndexOrderedSet(self.configuration['addons'])
        self.configuration['git'] = OrderedSet(self.configuration['git'])

    def setdefault(self, key: str, default_value: Any, value_type: Optional[Type[Any]] = None):
        self.configuration.setdefault(key, default_value)
        value = self.configuration[key]
        if value and value_type and not isinstance(value, value_type):
            raise ValueError(f'Inccorect configuration value for parameter "{key}"')

    @classmethod
    def show_arguments_description(cls):
        return any(arg in ['-h', '--help'] for arg in sys.argv)


def parse_arguments() -> 'ArgumentParser':
    """Parse system arguments and initiate ERP arguments."""
    # Define argument parser
    parser = argparse.ArgumentParser(prog='MONSTER', description='All in one ERP')
    parser.add_argument(
        '-m', '--mode', dest='mode', type=str, default=Mode.STAGING.value,
        help='ERP mode, choose one of the following options: staging | production'
    )
    parser.add_argument(
        '-c', '--configuration', type=str, dest='configuration',
        help='Path to ERP configuration file in JSON format'
    )
    # Parse arguments and handle help request
    parsed_arguments = parser.parse_args(sys.argv[1:])
    if ArgumentParser.show_arguments_description():
        parser.print_help()
        return ArgumentParser(Mode.STAGING, {})
    else:
        # Load configuration from JSON file if specified
        configuration = {}
        if parsed_arguments.configuration:
            try:
                with open(parsed_arguments.configuration, 'r') as configuration_file:
                    configuration = json.loads(configuration_file.read())
            except Exception as error:
                logging.error(f"Error loading configuration file: {error}")
        return ArgumentParser(parsed_arguments.mode, configuration)


# Global variable to store parsed arguments
arguments = parse_arguments()
