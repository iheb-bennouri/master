import traceback
from typing import Optional
from . import exceptions
from . import tools
from . import config
from . import core

connectors: Optional[core.db.RedisManager] = None


def main():
    if config.parser.arguments.show_arguments_description():
        exit(1)
