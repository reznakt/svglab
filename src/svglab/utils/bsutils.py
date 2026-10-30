"""Utilities for working with BeautifulSoup."""

import xml.sax.saxutils
from collections.abc import Iterable, Sequence

import bs4
from typing_extensions import cast, override

from svglab.elements.names import ElementName
from svglab.serialize import get_current_formatter


class _BsFormatter(bs4.formatter.XMLFormatter):
    def __init__(self) -> None:
        formatter = get_current_formatter()
        super().__init__(
            # replaces special characters with XML entities (e.g. < -> &lt;)
            entity_substitution=bs4.formatter.EntitySubstitution.substitute_xml,
            indent=formatter.indent,
        )

    @override
    def attribute_value(self, value: str) -> str:
        # escaped by `quoted_attribute_value()`
        return value

    @classmethod
    @override
    def quoted_attribute_value(cls, value: str) -> str:
        # unlike bs4, this also writes tabs and line breaks as character
        # references, which an XML parser would otherwise turn into spaces
        return xml.sax.saxutils.quoteattr(value)

    @override
    def attributes(self, tag: bs4.Tag) -> Iterable[tuple[str, str]]:
        formatter = get_current_formatter()
        order: Sequence[str] = []

        if tag.name in formatter.attribute_order:
            order = formatter.attribute_order[cast(ElementName, tag.name)]
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

    Raises:
        TypeError: If `element` is neither a `Tag` nor a `NavigableString`.

    """
    result: str

    match element, pretty:
        case bs4.NavigableString(), _:
            result = _make_soup(element).decode(formatter=_BsFormatter())
        case bs4.Tag(), True:
            soup = _make_soup(element)

            result = soup.prettify(formatter=_BsFormatter())
        case bs4.Tag(), False:
            result = element.decode(formatter=_BsFormatter())
        case _:
            msg = f"Unsupported type: {type(element)}"
            raise TypeError(msg)

    return result.strip()
