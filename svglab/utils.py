import collections
import functools
from collections.abc import Generator, Iterable

import bs4
from typing_extensions import TypeVar
from useful_types import SupportsRichComparisonT


_T = TypeVar("_T")


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


def get_all_subclasses(
    cls: type[_T], /
) -> Generator[type[_T], None, None]:
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
