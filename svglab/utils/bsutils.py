"""Utilities for working with BeautifulSoup."""

from collections.abc import Iterable

import bs4
from typing_extensions import Any, cast, override

from svglab import serialize
from svglab.elements import names


class _BsFormatter(bs4.formatter.XMLFormatter):
    def __init__(self) -> None:
        formatter = serialize.get_current_formatter()
        super().__init__(
            # replaces special characters with XML entities (e.g. < -> &lt;)
            entity_substitution=bs4.formatter.EntitySubstitution.substitute_xml,
            indent=formatter.indent,
        )

    @override
    def attributes(self, tag: bs4.Tag) -> Iterable[tuple[str, Any]]:
        formatter = serialize.get_current_formatter()
        order = []

        if tag.name in formatter.attribute_order:
            order = formatter.attribute_order[
                cast(names.ElementName, tag.name)
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


def _make_soup(element: bs4.PageElement, /) -> bs4.BeautifulSoup:
    soup = bs4.BeautifulSoup()
    soup.append(element)
    return soup


def beautifulsoup_to_str(
    element: bs4.PageElement, /, *, pretty: bool
) -> str:
    """Convert a BeautifulSoup PageElement to a string.

    The current formatter settings are used to format the output.

    Args:
        element: The BeautifulSoup PageElement to convert.
        pretty: If `True`, the output will be pretty-printed.
            If `False`, the output will be a single line.

    Returns:
        The string representation of the PageElement.

    """
    result: str

    match element, pretty:
        case bs4.NavigableString(), _:
            result = _make_soup(element).decode(formatter=_BsFormatter())
        case bs4.Tag(), True:
            soup = _make_soup(element)

            result = soup.prettify(formatter=_BsFormatter())
        case bs4.Tag(), False:
            result = str(element)
        case _:
            msg = f"Unsupported type: {type(element)}"
            raise TypeError(msg)

    return result.strip()
