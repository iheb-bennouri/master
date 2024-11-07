from typing import Any, Type


def _get_mangled_method_name(klass: Type[Any], method_name: str) -> str:
    """
    Returns the mangled method name if the method name starts with double underscores.
    Otherwise, returns the original method name.
    :param klass: The class or instance for which to mangle the method name.
    :param method_name: The original method name.
    :return: The mangled method name if applicable, otherwise the original method name.
    """
    if method_name.startswith('__') and not method_name.endswith('__'):
        # Adjust for name-mangling (prepend _ClassName to method name)
        class_name = klass.__class__.__name__ if isinstance(klass, object) else klass.__name__
        return f"_{class_name}{method_name}"
    return method_name


def has_method(klass: Type[Any], method_name: str) -> bool:
    """
    Checks if a class or instance has a method with the given name.
    :param klass: The class or instance to check.
    :param method_name: The name of the method to look for.
    :return: True if the method exists and is callable, False otherwise.
    """
    # Use the mangled method name if applicable
    method_name = _get_mangled_method_name(klass, method_name)
    return hasattr(klass, method_name) and callable(getattr(klass, method_name))


def call_method(klass: Type[Any], method_name: str, *args, **kwargs) -> Any:
    """
    Calls a method on a class or instance if it exists, handling name-mangled methods.
    :param klass: The class or instance to call the method on.
    :param method_name: The name of the method to call.
    :param args: Positional arguments for the method.
    :param kwargs: Keyword arguments for the method.
    :return: The result of the method call if it exists, otherwise None.
    """
    # Get the potentially mangled method name
    method_name = _get_mangled_method_name(klass, method_name)
    # Check and call the method if it exists
    if has_method(klass, method_name):
        return getattr(klass, method_name)(*args, **kwargs)
    return None
