from ..tools.enums import Enum
import logging
from typing import List, Dict, Optional, Union
from .parser import arguments


class LoggerType(Enum):
    CRITICAL = logging.CRITICAL
    FATAL = logging.FATAL
    ERROR = logging.ERROR
    WARNING = logging.WARNING
    WARN = logging.WARN
    INFO = logging.INFO
    DEBUG = logging.DEBUG
    NOTSET = logging.NOTSET


def add_handler(handler: logging.Handler, add_default: bool = True):
    assert handler, 'Parameter "handler" is required'
    if add_default:
        handler.setLevel(level)
        handler.setFormatter(logging.Formatter(log_format))
    handlers.append(handler)


_argument_level: str = arguments.configuration.get('log_level', None)
level: int = LoggerType.DEBUG.value
if _argument_level:
    level: int = LoggerType.from_value(_argument_level).value
log_format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(level=level, format=log_format)
handlers: List[logging.Handler] = []
_argument_file: str = arguments.configuration.get('log_file', None)
if _argument_file:
    add_handler(logging.FileHandler(_argument_file))
else:
    add_handler(logging.StreamHandler())
loggers: Dict[str, logging.Logger] = {}


def get_logger(name: str, custom_handlers: Optional[Union[List[logging.Handler], logging.Handler]] = None) -> logging.Logger:
    assert name, 'Parameter "name" is required'
    if name in loggers:
        return loggers[name]
    loggers[name] = logging.getLogger(name)
    if loggers[name].hasHandlers() and (handlers or custom_handlers):
        loggers[name].handlers.clear()
    logger_handlers = handlers
    if custom_handlers:
        if not isinstance(custom_handlers, list):
            custom_handlers = [custom_handlers]
        logger_handlers = custom_handlers
    for handler in logger_handlers:
        loggers[name].addHandler(handler)
    return loggers[name]
