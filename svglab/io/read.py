from bs4 import BeautifulSoup as _BeautifulSoup

from svglab.types import SupportsRead

__all__ = ["parse_svg"]


class BeautifulSoup(_BeautifulSoup):
    def __init__(
        self, markup: str | bytes | SupportsRead[str] | SupportsRead[bytes] = ""
    ) -> None:
        super().__init__(markup=markup, features="lxml-xml")


def parse_svg(
    markup: str | bytes | SupportsRead[str] | SupportsRead[bytes],
) -> BeautifulSoup:
    return BeautifulSoup(markup)
