import collections
import functools
import math
import re
from collections.abc import Callable, Generator, Iterable, Sequence, Sized

import bs4
from typing_extensions import (
    Any,
    Literal,
    SupportsFloat,
    SupportsIndex,
    TypeAlias,
    TypeIs,
    TypeVar,
    cast,
    overload,
    override,
)
from useful_types import SupportsRichComparisonT

from svglab import constants, serialize
from svglab.elements import names


_T = TypeVar("_T")
_DT = TypeVar("_DT")
_NT = TypeVar("_NT")

_Map: TypeAlias = Callable[[_T], _NT]


class BsFormatter(bs4.formatter.XMLFormatter):
    def __init__(self) -> None:
        formatter = serialize.get_current_formatter()
        super().__init__(indent=formatter.indent)

    @override
    def attributes(self, tag: bs4.Tag) -> Iterable[tuple[str, Any]]:
        formatter = serialize.get_current_formatter()
        order = []

        if tag.name in formatter.attribute_order:
            order = formatter.attribute_order[
                cast(names.TagName, tag.name)
            ]
        elif "*" in formatter.attribute_order:
            order = formatter.attribute_order["*"]

        order_index = {attr: i for i, attr in enumerate(order)}
        order_length = len(order)

        # first sort by the predefined order, then by name
        return sorted(
            tag.attrs.items(),
            key=lambda item: (
                order_index.get(item[0], order_length),
                item[0],
            ),
        )


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


def beautifulsoup_to_str(
    element: bs4.PageElement, /, *, pretty: bool
) -> str:
    result: str

    match element, pretty:
        case bs4.NavigableString(), _:
            result = str(make_soup(element))
        case bs4.Tag(), True:
            soup = make_soup(element)

            result = soup.prettify(formatter=BsFormatter())
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
    """Check if two floating-point numbers are almost equal.

    Args:
        a: The first number to compare.
        b: The second number to compare.

    Returns:
        `True` if the two numbers are almost equal, `False` otherwise.

    Examples:
        import math
        >>> is_close(1.0, 1.0)
        True
        >>> is_close(1.0, 1.0 + 1e-20)
        True
        >>> is_close(1.0, 1.0 + 0.001)
        False
        >>> is_close(0, math.sin(math.pi))
        True

    """
    return math.isclose(
        a,
        b,
        rel_tol=constants.FLOAT_RELATIVE_TOLERANCE,
        abs_tol=constants.FLOAT_ABSOLUTE_TOLERANCE,
    )


@overload
def apply_single_or_many(func: _Map[_T, _NT], value: _T, /) -> _NT: ...


@overload
def apply_single_or_many(
    func: _Map[_T, _NT], first: _T, second: _T, /, *values: _T
) -> tuple[_NT, ...]: ...


def apply_single_or_many(
    func: _Map[_T, _NT], /, *values: _T
) -> _NT | tuple[_NT, ...]:
    """Apply a function to one or more values.

    Args:
        func: The function to apply.
        values: The values to apply the function to.

    Returns:
        The result of applying the function to the value, or a tuple of
        such results if multiple values are provided.

    Examples:
        >>> apply_single_or_many(str, 1)
        '1'
        >>> apply_single_or_many(str, 1, 2, 3)
        ('1', '2', '3')

    """
    result = tuple(map(func, values))

    return result[0] if len(result) == 1 else result


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

    if match is None:
        return None

    return match.group(1), match.group(2)


def tan(degrees: float) -> float:
    """Compute the tangent of an angle in degrees.

    This function is a wrapper around `math.tan` that takes an angle in degrees
    and returns "nice" values for common angles.

    Args:
        degrees: The angle in degrees.

    Returns:
        The tangent of the angle.

    Examples:
        >>> tan(0)
        0
        >>> tan(45)
        1

    """
    degrees %= 180

    match degrees:
        case 0:
            return 0
        case 45:
            return 1
        case 135:
            return -1
        case _:
            return math.tan(math.radians(degrees))


def arctan(value: float) -> float:
    """Compute the arctangent of a value in degrees.

    This function is a wrapper around `math.atan` that returns "nice" values
    for common inputs. The output is in degrees.

    Args:
        value: The value to compute the arctangent of.

    Returns:
        The arctangent of the value in degrees.

    Examples:
        >>> arctan(0)
        0
        >>> arctan(1)
        45

    """
    match value:
        case 0:
            return 0
        case 1:
            return 45
        case -1:
            return -45
        case _:
            return math.degrees(math.atan(value))


def degrees(radians: float) -> float:
    """Convert radians to degrees, returning a value in the range (-180, 180].

    Args:
        radians: The angle in radians.

    Returns:
        The angle in degrees in the range (-180, 180].

    Examples:
        >>> from math import pi
        >>> degrees(0)
        0.0
        >>> degrees(pi)
        180.0
        >>> degrees(2 * pi)
        0.0
        >>> degrees(-pi / 2)
        -90.0
        >>> degrees(-pi)
        180.0

    """
    deg = math.degrees(radians)
    normalized = ((deg + 180) % 360) - 180

    if is_close(normalized, -180):
        return 180.0

    return normalized


def signum(x: float) -> Literal[-1, 0, 1]:
    """Compute the signum function `sgn(x)`.

    Args:
        x: The value to compute the signum of.

    Returns:
        -1 if the value is negative, 0 if the value is zero, and 1 if the value
        is positive.

    Examples:
        >>> signum(-5)
        -1
        >>> signum(0)
        0
        >>> signum(0.5)
        1

    """
    if x < 0:
        return -1

    if x > 0:
        return 1

    return 0


def arccos(value: float) -> float:
    """Compute the arccosine of a value in degrees.

    This function is a wrapper around `math.acos` that returns "nice" values
    for common inputs. The output is in degrees.

    Args:
        value: The value to compute the arccosine of.

    Returns:
        The arccosine of the value in degrees.

    Examples:
        >>> arccos(1)
        0
        >>> arccos(0)
        90

    """
    match value:
        case 1:
            return 0
        case 0:
            return 90
        case _:
            return math.degrees(math.acos(value))
