from . import exceptions
from . import tools
from . import config
from . import core


def main():
    if config.parser.arguments.show_arguments_description():
        exit(1)
