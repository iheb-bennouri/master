import enum
from typing import Any


class Enum(enum.Enum):
    @classmethod
    def from_value(cls, value: Any) -> 'Enum':
        """
        Returns the enum member corresponding to the given value.
        Args:
            value: The value to look up in the enum.
        Raises:
            ValueError: If no matching enum member is found.
        """
        for member in cls:
            if member.value == value:
                return member
        raise ValueError(f'{value} is not a valid value for {cls.__name__}')
