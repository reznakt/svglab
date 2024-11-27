from typing import cast

import bs4

from svglab.elements import Svg

from .utils import SupportsRead


class BeautifulSoup(bs4.BeautifulSoup):
    """A wrapper around `bs4.BeautifulSoup` that uses the `lxml-xml` parser."""

    def __init__(
        self, markup: str | bytes | SupportsRead[str] | SupportsRead[bytes] = ""
    ) -> None:
        super().__init__(markup=markup, features="lxml-xml")


def parse_svg(markup: str | bytes | SupportsRead[str] | SupportsRead[bytes]) -> Svg:
    """Parse an SVG document.

    The document must be a valid XML document containing a single SVG document fragment.

    Args:
        markup: A string or a file-like object representing markup to be parsed.

    Returns:
        The parsed SVG document in the form of an `Svg` instance.

    Raises:
        ValueError: If the markup does not contain a single SVG document fragment

    Examples:
        >>> svg = parse_svg("<svg><rect/></svg>")
        >>> type(svg).__name__
        'Svg'
        >>> len(svg.children)
        1

    """
    soup = BeautifulSoup(markup)

    svg_fragment_count = len(soup.find_all("svg", recursive=False))

    if svg_fragment_count != 1:
        msg = (
            f"Expected 1 <svg> element, found {svg_fragment_count}."
            " This does not look like a valid SVG."
        )

        raise ValueError(msg)

    return Svg(_backend=cast(bs4.Tag, soup.svg))
