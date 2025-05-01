"""Miscellaneous utility functions that don't fit anywhere else."""

import re
from collections.abc import Generator

from typing_extensions import TypeIs, TypeVar


_T = TypeVar("_T")


def get_all_subclasses(cls: type[_T], /) -> Generator[type[_T]]:
    """Recursively obtain all subclasses of a class.

    Args:
        cls: The class to obtain subclasses for.

    Yields:
        Subclasses of the given class, including subclasses of subclasses
        (and so on).

    Examples:
        >>> class A:
        ...     pass
        >>> class B(A):
        ...     pass
        >>> class C(B):
        ...     pass
        >>> list(cls.__name__ for cls in get_all_subclasses(A))
        ['B', 'C']

    """
    for subclass in cls.__subclasses__():
        yield subclass
        yield from get_all_subclasses(subclass)


def basic_compare(other: object, /, *, self: _T) -> TypeIs[_T]:
    """Perform a basic comparison between two objects.

    This is a helper function for implementing the `__eq__` method.

    It checks if the other object is the same as the current object or
    an instance of the same class.

    Args:
        other: The other object to compare.
        self: The current object.

    Returns:
        `True` if the other object is the same as the current object or an
        instance of the same class, `False` otherwise.

    Examples:
        >>> class A:
        ...     def __eq__(self, other: object, /) -> bool:
        ...         return basic_compare(other, self=self)
        >>> A() == A()
        True
        >>> A() == 1
        False

    """
    return other is self or isinstance(other, type(self))


def extract_function_name_and_args(attr: str) -> tuple[str, str] | None:
    """Extract function name and arguments from a function-call-like attribute.

    An attribute is considered to be a function call if it has the form
    `name(args)`. This function extracts the name and the arguments from such
    an attribute. If the attribute is not a function call, `None` is returned.

    Args:
    attr: The attribute to extract the function name and arguments from.

    Returns:
    A tuple containing the function name and the arguments,
    or `None` if the attribute is not a function call.

    Examples:
    >>> extract_function_name_and_args("foo()") is None  # no arguments
    True
    >>> extract_function_name_and_args("foo(42)")
    ('foo', '42')
    >>> extract_function_name_and_args("foo(42, 'bar')")
    ('foo', "42, 'bar'")
    >>> extract_function_name_and_args(
    ...     "bar"
    ... ) is None  # not a function call
    True

    """
    match = re.match(r"^([^\(\)]+)\(([^\(\)]+)\)$", attr)

    return None if match is None else (match[1], match[2])
