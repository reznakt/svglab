from typing import cast

import bs4

from svglab.elements import Svg

from .utils import SupportsRead


class BeautifulSoup(bs4.BeautifulSoup):
    def __init__(
        self, markup: str | bytes | SupportsRead[str] | SupportsRead[bytes] = ""
    ) -> None:
        super().__init__(markup=markup, features="lxml-xml")


def parse_soup(
    markup: str | bytes | SupportsRead[str] | SupportsRead[bytes],
) -> BeautifulSoup:
    return BeautifulSoup(markup)


def parse_svg(
    markup: str | bytes | SupportsRead[str] | SupportsRead[bytes],
) -> Svg:
    soup = parse_soup(markup)

    svg_fragment_count = len(soup.find_all("svg", recursive=False))

    if svg_fragment_count != 1:
        msg = (
            f"Expected 1 <svg> element, found {svg_fragment_count}."
            "This does not look like a valid SVG."
        )

        raise ValueError(msg)

    return Svg(_backend=cast(bs4.Tag, soup.svg))
