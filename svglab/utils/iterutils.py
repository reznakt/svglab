"""Utilities for working with iterables."""

import functools
from collections.abc import Generator, Iterable, Sequence

from typing_extensions import Sized, SupportsIndex, TypeVar


_T = TypeVar("_T")
_DT = TypeVar("_DT")


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


def search_by_reference(sequence: Iterable[_T], item: _T) -> int:
    """Search for an item in a sequence by reference.

    Args:
        sequence: The sequence to search.
        item: The item to find.

    Returns:
        The index of the item in the sequence.

    Raises:
        ValueError: If the item is not found in the sequence.

    Examples:
        >>> search_by_reference([1, 2, 3], 2)
        1
        >>> search_by_reference([1, 2, 3], 4)
        Traceback (most recent call last):
            ...
        ValueError: Item not found in sequence: 4

    """
    for i, x in enumerate(sequence):
        if x is item:
            return i

    msg = f"Item not found in sequence: {item!r}"
    raise ValueError(msg)


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
    idx = search_by_reference(sequence, item)

    if idx == 0:
        msg = f"Item {item!r} has no predecessor."
        raise ValueError(msg)

    return sequence[idx - 1]


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
