from collections import deque
from typing import Literal, TypeAlias

import bs4
from bs4 import BeautifulSoup

from svglab.elements import Svg

from .utils import SupportsRead

Parser: TypeAlias = Literal["html.parser", "lxml", "lxml-xml", "html5lib"]


def get_root_svg_fragments(soup: bs4.Tag) -> list[bs4.Tag]:
    queue = deque([soup])

    while queue:
        node = queue.popleft()

        svg_fragments = node.find_all("svg")

        if svg_fragments:
            return svg_fragments

        queue.extend(child for child in node.children if isinstance(child, bs4.Tag))

    return []


def parse_svg(
    markup: str | bytes | SupportsRead[str] | SupportsRead[bytes],
    /,
    *,
    parser: Parser = "lxml-xml",
) -> Svg:
    """Parse an SVG document.

    The document must be a valid XML document containing a single SVG document fragment.

    Args:
        markup: A string or a file-like object representing markup to be parsed.
        parser: The name of the parser to use. Defaults to 'lxml-xml'.

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
    soup = BeautifulSoup(markup, features=parser)

    svg_fragments = get_root_svg_fragments(soup)

    if len(svg_fragments) != 1:
        msg = (
            f"Expected 1 <svg> element, found {len(svg_fragments)}."
            " This does not look like a valid SVG."
        )

        raise ValueError(msg)

    return Svg(_backend=svg_fragments[0])
