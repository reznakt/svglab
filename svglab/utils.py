import collections
import functools
import math
from collections.abc import Generator, Iterable, Sequence, Sized

import bs4
from typing_extensions import (
    SupportsFloat,
    SupportsIndex,
    TypeAlias,
    TypeIs,
    TypeVar,
)
from useful_types import SupportsRichComparisonT

from svglab import constants


_T = TypeVar("_T")
_DT = TypeVar("_DT")

_NestedIterableItem: TypeAlias = _T | Iterable["_NestedIterableItem[_T]"]
_NestedIterable: TypeAlias = Iterable[_NestedIterableItem[_T]]


def is_empty(iterable: Iterable[object], /) -> bool:
    """Determine whether an iterable is empty.

    Args:
        iterable: The iterable to check.

    Returns:
        `True` if the iterable is empty, `False` otherwise.

    Examples:
        >>> is_empty([])
        True
        >>> is_empty([1, 2, 3])
        False
        >>> is_empty(range(0))
        True
        >>> is_empty(range(3))
        False

    """
    for _ in iterable:
        return False

    return True


def length(iterable: Iterable[_T], /) -> int:
    """Count the number of items in an iterable.

    Args:
        iterable: The iterable to count.

    Returns:
        The number of items in the iterable.

    Examples:
        >>> length([])
        0
        >>> length([1, 2, 3])
        3
        >>> length(range(0))
        0
        >>> length(range(3))
        3

    """
    return sum(1 for _ in iterable)


def take_last(iterable: Iterable[_T], /) -> _T | None:
    """Get the last item in an iterable.

    Args:
        iterable: The iterable to extract the last item from.

    Returns:
        The last item in the iterable, or `None` if the iterable is empty.

    Examples:
        >>> take_last([]) is None
        True
        >>> take_last([1, 2, 3])
        3
        >>> take_last(range(0)) is None
        True
        >>> take_last(range(3))
        2

    """
    return functools.reduce(lambda _, s: s, iterable, None)


def make_soup(element: bs4.PageElement, /) -> bs4.BeautifulSoup:
    soup = bs4.BeautifulSoup()
    soup.append(element)
    return soup


def get_formatter(*, indent: int) -> bs4.formatter.Formatter:
    if indent < 0:
        raise ValueError("Indent must be a non-negative integer.")

    return bs4.formatter.XMLFormatter(indent=indent)


def beautifulsoup_to_str(
    element: bs4.PageElement, /, *, pretty: bool, indent: int
) -> str:
    result: str

    match element, pretty:
        case bs4.NavigableString(), _:
            result = str(make_soup(element))
        case bs4.Tag(), True:
            formatter = get_formatter(indent=indent)
            soup = make_soup(element)

            result = soup.prettify(formatter=formatter)
        case bs4.Tag(), False:
            result = str(element)
        case _:
            msg = f"Unsupported type: {type(element)}"
            raise TypeError(msg)

    return result.strip()


def clamp(
    value: SupportsRichComparisonT,
    /,
    *,
    min_value: SupportsRichComparisonT,
    max_value: SupportsRichComparisonT,
) -> SupportsRichComparisonT:
    """Clamp a value between two bounds.

    Args:
        value: The value to clamp.
        min_value: The minimum value.
        max_value: The maximum value.

    Returns:
        The clamped value. If `value` is less than `min_value`, `min_value` is
        returned. If `value` is greater than `max_value`, `max_value` is
        returned. Otherwise, `value` is returned.

    Examples:
        >>> clamp(5, min_value=0, max_value=10)
        5
        >>> clamp(-5, min_value=0, max_value=10)
        0
        >>> clamp(15, min_value=0, max_value=10)
        10

    """
    return max(min(value, max_value), min_value)


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
    queue = collections.deque([cls])

    while queue:
        subclass = queue.popleft()

        if subclass is not cls:
            yield subclass

        queue.extend(subclass.__subclasses__())


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


def flatten(iterable: _NestedIterable[_T], /) -> Generator[_T]:
    """Flatten a nested iterable.

    Args:
        iterable: The nested iterable to flatten.

    Yields:
        Items from the nested iterable, in order.

    Examples:
        >>> list(flatten([]))
        []
        >>> list(flatten([1, 2, 3]))
        [1, 2, 3]
        >>> list(flatten([[1, 2], [3, 4]]))
        [1, 2, 3, 4]
        >>> list(flatten([1, [2, 3], 4]))
        [1, 2, 3, 4]
        >>> list(flatten([1, [2, [3, [4]]]]))
        [1, 2, 3, 4]

    """
    for item in iterable:
        yield from flatten(item) if isinstance(item, Iterable) else (item,)


def prev(sequence: Sequence[_T], item: _T) -> _T:
    """Get the item before a given item in a sequence.

    Args:
        sequence: The sequence to search.
        item: The item to find the predecessor of.

    Returns:
        The item before the given item in the sequence.

    Raises:
        ValueError: If the item is not found in the sequence or if the item


    Examples:
        >>> prev([1, 2, 3], 2)
        1
        >>> prev([1, 2, 3], 1)
        Traceback (most recent call last):
            ...
        ValueError: Item 1 has no predecessor.
        >>> prev([1, 2, 3], 4)
        Traceback (most recent call last):
            ...
        ValueError: Item not found in sequence: 4

    """
    try:
        index = sequence.index(item)
    except ValueError as e:
        msg = f"Item not found in sequence: {item!r}"
        raise ValueError(msg) from e

    if index == 0:
        msg = f"Item {item!r} has no predecessor."
        raise ValueError(msg)

    return sequence[index - 1]


def pairwise(
    iterable: Iterable[_T], /, default: _DT = None
) -> Generator[tuple[_T | _DT, _T]]:
    """Iterate over pairs of items in an iterable.

    Args:
        iterable: The iterable to iterate over.
        default: The default value to use for the first item.

    Yields:
        Pairs of items from the iterable. The first item in each pair is the
        previous item, or the default value if the first item is yielded.

    Examples:
        >>> list(pairwise([]))
        []
        >>> list(pairwise([1]))
        [(None, 1)]
        >>> list(pairwise([1, 2]))
        [(None, 1), (1, 2)]
        >>> list(pairwise([1, 2, 3]))
        [(None, 1), (1, 2), (2, 3)]

    """
    prev_item = default

    for item in iterable:
        yield prev_item, item
        prev_item = item


def is_first_index(sized: Sized, index: SupportsIndex) -> bool:
    """Check if an index resolves to the first index in a `Sized` object.

    Args:
        sized: The `Sized` object to check.
        index: The index to check.

    Returns:
        `True` if the index is the first index in the `Sized` object,
        `False` otherwise.

    Examples:
        >>> is_first_index([1, 2, 3], 0)
        True
        >>> is_first_index([1, 2, 3], 1)
        False
        >>> is_first_index([1, 2, 3], -1)
        False
        >>> is_first_index([1, 2, 3], -3)
        True
        >>> is_first_index([], 0)
        True

    """
    start, *_ = slice(index, index).indices(len(sized))

    return start == 0


def is_close(
    a: SupportsFloat | SupportsIndex, b: SupportsFloat | SupportsIndex, /
) -> bool:
    return math.isclose(
        a,
        b,
        rel_tol=constants.FLOAT_RELATIVE_TOLERANCE,
        abs_tol=constants.FLOAT_ABSOLUTE_TOLERANCE,
    )
