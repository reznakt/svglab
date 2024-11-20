from os import PathLike

from atomicwrites import atomic_write
from bs4 import BeautifulSoup

__all__ = ["write_svg"]


def write_svg(soup: BeautifulSoup, path: str | PathLike[str]) -> None:
    path = str(path)

    with atomic_write(path, overwrite=True) as file:
        file.write(soup.prettify())
