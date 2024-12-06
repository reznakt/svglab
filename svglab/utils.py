from collections.abc import Iterable

import bs4


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
