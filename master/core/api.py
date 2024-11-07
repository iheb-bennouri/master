from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Optional, Any, Type
from master.config.logging import get_logger
from master.tools.misc import call_method

_logger = get_logger(__name__)
classes = defaultdict(list)


class AbstractMeta(ABC):
    @classmethod
    @abstractmethod
    def attach_element(cls, *args, **kwargs):
        pass


class Meta(AbstractMeta, type):
    def __new__(cls, *args, **kwargs):
        klass = type(*args, **kwargs)
        cls.attach_element(klass)
        call_method(klass, '_attach_klass')
        return klass

    @classmethod
    def attach_element(cls, klass: Type[Any]):
        meta_path: Optional[str] = getattr(klass, '__meta_path__', None)
        if not meta_path:
            classes['_'].append(klass)
        else:
            classes[meta_path].append(klass)
