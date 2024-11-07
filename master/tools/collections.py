from collections import OrderedDict
from collections.abc import Iterable
from typing import Any, Optional, Dict


def is_complex_iterable(obj: Any) -> bool:
    """Check if the object is iterable but exclude strings and basic numbers (int, float)."""
    return isinstance(obj, Iterable) and not isinstance(obj, (str, int, float))


class OrderedSet(Iterable):
    """
    A set that preserves the insertion order of elements.
    Attributes:
        _data (OrderedDict): An ordered dictionary to store the elements as keys.
    """
    __slots__ = '_data'

    def __init__(self, iterable: Optional[Iterable[Any]] = None):
        """
        Initializes an OrderedSet, optionally with elements from an iterable.
        Args:
            iterable (Optional[Iterable[Any]]): An optional iterable to initialize the set with.
        """
        self._data = OrderedDict()
        if iterable:
            if is_complex_iterable(iterable):
                self.update(iterable)
            else:
                self.add(iterable)

    def add(self, value: Any) -> None:
        """
        Adds an element to the set, maintaining order and uniqueness.
        Args:
            value (Any): The element to add.
        """
        self._data[value] = None

    def update(self, iterable: Iterable[Any]) -> None:
        """
        Adds multiple elements from an iterable to the set.
        Args:
            iterable (Iterable[Any]): The iterable containing elements to add.
        Raises:
            AssertionError: If the input is not a complex iterable.
        """
        assert is_complex_iterable(iterable), "Provided value must be a complex iterable."
        for value in iterable:
            self.add(value)

    def copy(self) -> 'OrderedSet':
        """
        Returns a shallow copy of the OrderedSet.
        Returns:
            OrderedSet: A new instance with the same elements.
        """
        return self.__class__(self._data.keys())

    def index(self, item: Any) -> int:
        """
        Returns the index of the specified item in the set.
        Args:
            item (Any): The item to find the index for.
        Returns:
            int: The index of the item, or -1 if not found.
        """
        for index, current in enumerate(self._data.keys()):
            if current == item:
                return index
        return -1

    def remove(self, item: Any) -> None:
        """
        Removes the specified item from the set.
        Args:
            item (Any): The item to remove.
        Raises:
            KeyError: If the item is not in the set.
        """
        del self._data[item]

    def __getitem__(self, index: int) -> Any:
        """
        Gets the element at the specified index.
        Args:
            index (int): The index of the element.
        Returns:
            Any: The element at the given index.
        """
        return list(self._data.keys())[index]

    def __add__(self, other: 'OrderedSet') -> 'OrderedSet':
        """
        Returns a new OrderedSet containing elements of this set followed by elements of another set.
        Args:
            other (OrderedSet): Another OrderedSet to add.
        Returns:
            OrderedSet: A new OrderedSet with combined elements.
        """
        assert isinstance(other, OrderedSet), 'Incorrect value type for addition'
        return OrderedSet(list(self._data.keys()) + list(other._data.keys()))

    def __sub__(self, other: 'OrderedSet') -> 'OrderedSet':
        """
        Returns a new OrderedSet with elements that are in this set but not in the other.
        Args:
            other (OrderedSet): Another OrderedSet to subtract.
        Returns:
            OrderedSet: A new OrderedSet with the difference.
        """
        assert isinstance(other, OrderedSet), 'Incorrect value type for subtraction'
        return OrderedSet([value for value in self if value not in other])

    def __contains__(self, value: Any) -> bool:
        """Checks if the value is in the set."""
        return value in self._data

    def __iter__(self):
        """Returns an iterator over the set elements."""
        return iter(self._data.keys())

    def __reversed__(self):
        """Returns a reverse iterator over the set elements."""
        return reversed(self._data.keys())

    def __repr__(self) -> str:
        """Returns a string representation of the OrderedSet."""
        return f"OrderedSet({list(self._data.keys())})"

    def __len__(self) -> int:
        """Returns the number of elements in the set."""
        return len(self._data)

    def __eq__(self, other: Any) -> bool:
        """
        Checks if this OrderedSet is equal to another OrderedSet or list.
        Args:
            other (Any): The other object to compare.
        Returns:
            bool: True if equal, False otherwise.
        """
        if isinstance(other, OrderedSet):
            return list(self._data.keys()) == list(other._data.keys())
        elif isinstance(other, list):
            return list(self._data.keys()) == other
        elif isinstance(other, set):
            return list(self._data.keys()) == list(other)
        return False

    def __hash__(self) -> int:
        """Returns a hash based on the set's elements."""
        return hash(tuple(self._data.keys()))


class LastIndexOrderedSet(OrderedSet):
    """
    A subclass of OrderedSet that updates the position of an element to the end
    whenever it's added, effectively maintaining the most recent insertion order.

    This is useful in cases where elements should be re-ordered to reflect
    their most recent addition.
    """

    def add(self, value: Any) -> None:
        """
        Adds an element to the set, moving it to the end if it already exists.
        Args:
            value (Any): The element to add.
        """
        if value in self._data:
            self.remove(value)  # Remove the value if it already exists.
        super().add(value)  # Add it again, moving it to the end.

    def __repr__(self) -> str:
        """Returns a string representation of the LastIndexOrderedSet."""
        return f"LastIndexOrderedSet({list(self._data.keys())})"
