from os import PathLike

from atomicwrites import atomic_write
from bs4 import BeautifulSoup as _BeautifulSoup

from .types import SupportsRead

__all__ = ["parse_svg", "write_svg"]


class BeautifulSoup(_BeautifulSoup):
    def __init__(
        self, markup: str | bytes | SupportsRead[str] | SupportsRead[bytes] = ""
    ) -> None:
        super().__init__(markup=markup, features="lxml-xml")


def parse_svg(
    markup: str | bytes | SupportsRead[str] | SupportsRead[bytes],
) -> BeautifulSoup:
    return BeautifulSoup(markup)


__all__ = ["write_svg"]


def write_svg(soup: BeautifulSoup, path: str | PathLike[str]) -> None:
    path = str(path)

    with atomic_write(path, overwrite=True) as file:
        file.write(soup.prettify())
