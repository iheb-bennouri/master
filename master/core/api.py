from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Optional, Any, Type, List
from master.config.logging import get_logger
from master.tools.misc import call_classmethod

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
        call_classmethod(klass, '_attach_klass')
        return klass

    @classmethod
    def attach_element(cls, klass: Type[Any]):
        meta_path: Optional[str] = getattr(klass, '__meta_path__', None)
        if not meta_path:
            classes['_'].append(klass)
        else:
            classes[meta_path].append(klass)

    @classmethod
    def create_merged_class(cls, new_class_name: str, classes_list: List[Type[Any]]) -> Type[Any]:
        """
        Dynamically creates a new class that merges multiple classes.
        The new class respects the Method Resolution Order (MRO) for super() calls.
        :param new_class_name: New merged class name.
        :param classes_list: List of classes to merge.
        :return: A new class with combined functionality.
        """
        if not classes_list:
            raise ValueError("classes_list must contain at least one class to merge.")

        # Check for a common base class
        root_base = classes_list[0].__bases__[0]
        if not all(root_base in cls.__mro__ for cls in classes_list):
            raise TypeError("All classes must share the same root base class.")

        new_class = type(new_class_name, tuple(classes_list), {})

        _logger.debug(f"Created merged class '{new_class_name}' with bases: {[cls.__name__ for cls in classes_list]}")
        return new_class
