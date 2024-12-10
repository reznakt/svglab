from collections.abc import Iterable

import bs4
import readable_number


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


def format_number(
    number: float,
    /,
    *,
    max_precision: int | None = None,
) -> str:
    """Convert a `float` to a string.

    This function converts a `float` to a string,
    optimizing the output for human readability and compactness.

    Args:
        number: The number to format.
        max_precision: The maximum number of significant
        figures after the decimal point. Must be an integer
        greater than zero, or `None` to use as many as possible.
        The number will be rounded to the nearest value
        with the specified number of significant figures.

    Returns:
        The formatted number.

    Raises:
        ValueError: If `max_precision` is not positive.

    Examples:
        >>> format_number(123.456)
        '123.456'
        >>> format_number(123.456, max_precision=2)
        '123.46'
        >>> format_number(10.0)
        '10'
        >>> format_number(100000000)
        '1e+08'

    """
    if max_precision is not None and max_precision <= 0:
        raise ValueError("max_precision must be a positive integer.")

    rn = readable_number.ReadableNumber(
        digit_group_delimiter="",
        use_exponent_for_large_numbers=True,
        use_exponent_for_small_numbers=True,
        significant_figures_after_decimal_point=max_precision,
    )

    result = rn.of(number)
    assert type(result) is str

    return result
